import os
from src.mcts.engine import MCTSEngine
from src.llm.gemini_client import GeminiClient
from src.utils.logger import logger

def main():
    logger.info("Initializing CogniCode-MCTS Environment...")

    # 1. Configuration
    # Tries to load real key, falls back to Mock if not found
    api_key = os.getenv("GEMINI_API_KEY")
    client = GeminiClient(api_key=api_key)
    
    # 2. Define the Challenge
    # We want the agent to write a recursive factorial function.
    problem_description = "Write a recursive Python function named 'factorial' that calculates the factorial of a non-negative integer."
    
    # 3. Define the 'Ground Truth' (The invisible unit test)
    # The agent does not see this; the sandbox uses it to validate execution.
    test_harness = """
if __name__ == "__main__":
    try:
        assert factorial(5) == 120
        assert factorial(0) == 1
        assert factorial(3) == 6
    except NameError:
        exit(1) # Fail if function not defined
    except AssertionError:
        exit(1) # Fail if logic is wrong
"""

    # 4. Initialize Engine
    engine = MCTSEngine(client, problem_description, test_harness)
    
    # 5. Run Search
    logger.info(f"Problem: {problem_description}")
    final_code = engine.run(iterations=30)
    
    print("\n" + "="*40)
    print("🏆 FINAL GENERATED CODE")
    print("="*40)
    print(final_code)
    print("="*40)

if __name__ == "__main__":
    main()