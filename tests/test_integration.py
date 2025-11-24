import pytest
from src.mcts.engine import MCTSEngine
from src.llm.gemini_client import GeminiClient

def test_full_flow_mocked():
    """
    Tests the entire pipeline using the Mock LLM.
    Ensures that the tree search eventually finds the correct factorial implementation.
    """
    # 1. Setup Mock Client
    client = GeminiClient(mock_mode=True)
    
    # 2. Problem & Harness
    problem = "Write a factorial function."
    test_harness = """
if __name__ == "__main__":
    assert factorial(5) == 120
    assert factorial(0) == 1
"""

    # 3. Init Engine
    engine = MCTSEngine(client, problem, test_harness)
    
    # 4. Run Search
    result_code = engine.run(iterations=20)
    
    # 5. Assertions
    assert "def factorial(n):" in result_code
    assert "return n * factorial(n-1)" in result_code
    print("\nTest Passed: Agent successfully navigated the search tree.")

if __name__ == "__main__":
    test_full_flow_mocked()
