import os
import random
from typing import List
import google.generativeai as genai
from src.llm.abstract_client import AbstractLLMClient
from src.utils.logger import logger

class GeminiClient(AbstractLLMClient):
    def __init__(self, api_key: str = None, mock_mode: bool = False):
        self.mock_mode = mock_mode
        if not mock_mode:
            self.api_key = api_key or os.getenv("GEMINI_API_KEY")
            if not self.api_key:
                logger.warning("No API Key found. Switching to MOCK MODE.")
                self.mock_mode = True
            else:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate_candidates(self, problem: str, current_state: str, n: int = 3) -> List[str]:
        if self.mock_mode:
            return self._mock_generator(current_state, n)
        
        # Real API Implementation
        prompt = f"""
        You are a Python coding assistant.
        Problem: {problem}
        
        Current Code Context:
        {current_state}
        
        Instructions:
        1. Generate exactly {n} distinct continuations for the next logical step.
        2. Do not repeat code already in context.
        3. Output only the code, separated by '|||' delimiter.
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Naive parsing strategy - in prod this would be more robust
            candidates = response.text.split('|||')
            return [c.strip().replace('```python', '').replace('```', '') for c in candidates[:n]]
        except Exception as e:
            logger.error(f"API Error: {e}")
            return self._mock_generator(current_state, n)

    def _mock_generator(self, current_state: str, n: int) -> List[str]:
        """
        Simulates an LLM for testing without costs.
        Scenario: Writing a recursive factorial function.
        """
        candidates = []
        
        # State 0: Start
        if "def" not in current_state:
            return [
                "def factorial(n):",
                "def solve(n):", 
                "def fact(x):"
            ]
        
        # State 1: Inside Function
        if "factorial(n):" in current_state and "if" not in current_state:
            return [
                "    if n == 0: return 1",  # Correct path
                "    if n == 1: return 1",  # Okay path
                "    if n < 0: return None" # Defensive path
            ]
            
        # State 2: Recursive step
        if "return 1" in current_state and "return n" not in current_state:
            return [
                "    return n * factorial(n-1)", # Correct
                "    return n * factorial(n)",   # Infinite recursion (Bug)
                "    return n + factorial(n-1)"  # Logic bug
            ]
            
        return ["    pass"]
