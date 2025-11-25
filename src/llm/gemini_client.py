import os
import re
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
                self.model = genai.GenerativeModel('gemini-2.5-flash')

    def generate_candidates(self, problem: str, current_state: str, n: int = 3) -> List[str]:
        if self.mock_mode:
            return self._mock_generator(current_state, n)
        
        prompt = f"""
        You are an advanced Python Coding Engine.
        GOAL: {problem}
        
        CURRENT CODE CONTEXT:
        ```python
        {current_state}
        ```
        
        TASK:
        Generate exactly {n} distinct variations of the NEXT logical line(s) to continue the code.
        - **CRITICAL: You MUST include 4-space indentation if the context requires it (e.g., inside a function).**
        - The output must be syntactically correct Python.
        - DO NOT output the existing code.
        - Separate your {n} variations strictly using the delimiter "|||".
        
        VARIATIONS:
        """
        
        try:
            response = self.model.generate_content(prompt)
            raw_text = response.text
            
            cleaned_text = raw_text.replace("```python", "").replace("```", "")
            
            candidates = cleaned_text.split('|||')
            
            # We Use rstrip() instead of strip() to preserve leading whitespace for indentation!
            final_candidates = [c.rstrip() for c in candidates if c.strip()]
            
            if not final_candidates and cleaned_text.strip():
                final_candidates = [cleaned_text.rstrip()]
                
            return final_candidates[:n]
            
        except Exception as e:
            logger.error(f"API Error: {e}")
            return ["    pass # API Failure"]

    def _mock_generator(self, current_state: str, n: int) -> List[str]:
        # (Mock logic remains the same, but ensure indentation)
        if "def" not in current_state:
            return ["def factorial(n):"]
        if "factorial(n):" in current_state and "return" not in current_state:
            return ["    if n == 0: return 1"] 
        if "return 1" in current_state:
            return ["    return n * factorial(n-1)"]
        return ["    pass"]