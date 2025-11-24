import os
import time
import random
from typing import List
import google.generativeai as genai
from google.api_core import exceptions
from src.llm.abstract_client import AbstractLLMClient
from src.utils.logger import logger

class GeminiClient(AbstractLLMClient):
    """
    Implementation of the LLM Client using Google's Gemini 1.5.
    Includes robustness layers: Rate Limit handling and Mock Fallback.
    """
    
    def __init__(self, api_key: str = None, mock_mode: bool = False):
        self.mock_mode = mock_mode
        self.model_name = 'gemini-3-pro-preview' # Flash is faster/cheaper for high-iteration search
        
        if not mock_mode:
            self.api_key = api_key or os.getenv("GEMINI_API_KEY")
            if not self.api_key:
                logger.warning("No API Key found in env. Switching to MOCK MODE.")
                self.mock_mode = True
            else:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.model_name)

    def generate_candidates(self, problem: str, current_state: str, n: int = 3) -> List[str]:
        """
        Generates next-step candidates.
        Strategy: Try API -> Catch 429/RateLimit -> Wait/Retry -> Failover to Mock.
        """
        if self.mock_mode:
            return self._mock_generator(current_state, n)
        
        # 1. Construct a structural prompt to force easy-to-parse output
        prompt = f"""
        You are a generic coding completion engine.
        
        TASK:
        The user is solving this problem: "{problem}"
        
        CURRENT CODE STATE:
        ```python
        {current_state}
        ```
        
        INSTRUCTIONS:
        1. Generate exactly {n} distinct variations of the **next single logical line or block**.
        2. Do NOT repeat code that is already in the Current Code State.
        3. Do NOT wrap output in markdown (no ```python).
        4. Separate each variation strictly with the string "|||".
        5. If the code is complete, output "PASS".
        
        OUTPUT FORMAT:
        Variation 1 ||| Variation 2 ||| Variation 3
        """
        
        # 2. Resilience Loop (Exponential Backoff)
        max_retries = 3
        base_delay = 5 # seconds
        
        for attempt in range(max_retries):
            try:
                # Generate content
                response = self.model.generate_content(prompt)
                
                # Parse response
                raw_text = response.text
                candidates = raw_text.split('|||')
                
                # Clean up artifacts
                cleaned_candidates = [
                    c.strip().replace('```python', '').replace('```', '').replace('PASS', 'pass') 
                    for c in candidates
                ]
                
                # Ensure we have the requested number (pad if necessary)
                return cleaned_candidates[:n]
            
            except exceptions.ResourceExhausted:
                # HTTP 429: Rate Limit Hit
                wait_time = base_delay * (2 ** attempt) # 5s, 10s, 20s
                logger.warning(f"⚠️ API Rate Limit (429). Cooling down for {wait_time}s... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                
            except Exception as e:
                # Other errors (400, 500, Safety filters)
                logger.error(f"❌ API Error: {e}")
                break # Break loop to trigger fallback

        # 3. Failover
        logger.warning("📉 API Unavailable or Exhausted. Falling back to Local Mock Generator.")
        return self._mock_generator(current_state, n)

    def _mock_generator(self, current_state: str, n: int) -> List[str]:
        """
        Simulates an LLM for testing without costs or when API is down.
        Scenario: Writing a recursive factorial function.
        """
        # Scenario 1: Function Definition
        if "def" not in current_state:
            return [
                "def factorial(n):",
                "def solve(n):", 
                "def fact(x):"
            ]
        
        # Scenario 2: Base Case
        if "factorial(n):" in current_state and "if" not in current_state:
            return [
                "    if n == 0: return 1",  # Correct path
                "    if n == 1: return 1",  # Acceptable path
                "    if n < 0: return None" # Defensive path
            ]
            
        # Scenario 3: Recursive Step
        if "return 1" in current_state and "return n" not in current_state:
            return [
                "    return n * factorial(n-1)", # Correct
                "    return n * factorial(n)",   # Infinite recursion (Bug)
                "    return n + factorial(n-1)"  # Logic bug
            ]
            
        # Scenario 4: Done
        return ["    pass"]