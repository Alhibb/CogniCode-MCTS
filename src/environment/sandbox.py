import subprocess
import tempfile
import os
import sys
import ast
from typing import Dict, Any

class CodeSandbox:
    """
    Isolated execution environment. 
    Uses subprocess to prevent the agent from crashing the main thread.
    """
    
    @staticmethod
    def validate_syntax(code: str) -> bool:
        """Fast check to avoid spinning up processes for garbage code."""
        try:
            ast.parse(code)
            return True
        except SyntaxError:
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
            # We run the script in a separate python process
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=2.0 # Strict 2s timeout for infinite loops
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
                    "score": 0.0, 
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
            # Cleanup
            if os.path.exists(script_path):
                os.remove(script_path)
