import time
from src.mcts.engine import MCTSEngine
from src.llm.gemini_client import GeminiClient

def run_ablation():
    client = GeminiClient(mock_mode=True)
    problem = {
        "desc": "Write a recursive Python function named 'factorial' that calculates the factorial of a non-negative integer.",
        "seed": "def factorial(n):",
        "test": "assert factorial(5) == 120"
    }

    print("--- Ablation Study: Standard UCB1 vs. Neural-PUCT ---")
    
    # 1. Standard UCB1 (No Prior, No Heuristic)
    # We simulate this by mocking everything or tweaking engine
    
    # 2. Neural-PUCT
    print("\nRunning Neural-PUCT...")
    engine_neural = MCTSEngine(client, problem['desc'], problem['test'], starting_code=problem['seed'])
    result_neural = engine_neural.run(iterations=20)
    clean_result = result_neural.replace("\n", " ")
    print(f"Result (Neural): {clean_result}")

if __name__ == "__main__":
    run_ablation()
