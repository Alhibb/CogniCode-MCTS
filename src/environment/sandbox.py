import subprocess
import tempfile
import os
import sys
import ast
from typing import Dict, Any

class CodeSandbox:
    """
    Isolated execution environment. 
    """
    
    @staticmethod
    def validate_syntax(code: str) -> bool:
        """
        Checks if the code is syntactically valid.
        Handles 'incomplete' code (Unexpected EOF) by attempting to patch it.
        """
        try:
            ast.parse(code)
            return True
        except SyntaxError as e:
            # If the error is "unexpected EOF", it might just be incomplete
            # e.g., "def factorial(n):" is invalid, but "def factorial(n): pass" is valid.
            if e.msg.startswith("unexpected EOF") or e.msg.startswith("expected an indented block"):
                try:
                    # Attempt to patch with a pass statement to see if structure is valid
                    patched_code = code + "\n    pass"
                    ast.parse(patched_code)
                    return True
                except SyntaxError:
                    return False
            return False

    def execute(self, code: str, test_harness: str) -> Dict[str, Any]:
        """
        Executes code + tests.
        Returns: {success: bool, score: float, error_type: str, output: str}
        """
        # 1. AST Static Analysis
        if not self.validate_syntax(code):
            return {
                "success": False, 
                "score": -1.0, 
                "error_type": "syntax", 
                "output": "Syntax Error"
            }

        # 2. Prepare Payload
        full_script = f"{code}\n\n{test_harness}"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(full_script)
            script_path = f.name

        # 3. Execution with Timeout
        try:
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=2.0 
            )
            
            output = result.stdout + result.stderr
            
            if result.returncode == 0:
                return {
                    "success": True, 
                    "score": 1.0, 
                    "error_type": None, 
                    "output": output
                }
            else:
                return {
                    "success": False, 
                    "score": 0.0, # Neutral score for logic fail, but valid syntax
                    "error_type": "runtime", 
                    "output": output
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False, 
                "score": -0.5, 
                "error_type": "timeout", 
                "output": "Execution Timeout"
            }
        finally:
            if os.path.exists(script_path):
                os.remove(script_path)