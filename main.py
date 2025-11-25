import os
from src.mcts.engine import MCTSEngine
from src.llm.gemini_client import GeminiClient
from src.utils.logger import logger

def main():
    logger.info("Initializing CogniCode-MCTS Environment...")

    # 1. Configuration
    api_key = os.getenv("GEMINI_API_KEY")
    client = GeminiClient(api_key=api_key)
    
    # 2. Define the Challenge
    problem_description = "Write a recursive Python function named 'factorial' that calculates the factorial of a non-negative integer."
    
    # 3. Seed the Tree (Crucial for success)
    # We give the agent the function signature so it knows where to start.
    starting_code = "def factorial(n):"

    # 4. Define the 'Ground Truth' (The invisible unit test)
    test_harness = """
if __name__ == "__main__":
    try:
        # Test Case 1: Standard
        assert factorial(5) == 120, "Error on factorial(5)"
        # Test Case 2: Base case
        assert factorial(0) == 1, "Error on factorial(0)"
        # Test Case 3: Another check
        assert factorial(3) == 6, "Error on factorial(3)"
        
        print("ALL TESTS PASSED")
    except NameError:
        # Function doesn't exist yet
        exit(1) 
    except AssertionError as e:
        # Logic failed
        print(e)
        exit(1)
    except RecursionError:
        # Infinite loop caught
        exit(1)
"""

    # 5. Initialize Engine with Starting Code
    engine = MCTSEngine(client, problem_description, test_harness, starting_code=starting_code)
    
    # 6. Run Search
    logger.info(f"Problem: {problem_description}")
    logger.info(f"Seed: {starting_code}")
    
    # We give it 30 iterations to find the path
    final_code = engine.run(iterations=30)
    
    print("\n" + "="*40)
    print("🏆 FINAL GENERATED CODE")
    print("="*40)
    print(final_code)
    print("="*40)

if __name__ == "__main__":
    main()