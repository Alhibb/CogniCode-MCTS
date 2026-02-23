import time
import matplotlib.pyplot as plt
import numpy as np
from src.mcts.engine import MCTSEngine
from src.llm.gemini_client import GeminiClient

def run_benchmark(problems, iterations_list=[5, 10, 20, 30]):
    client = GeminiClient(mock_mode=True) # Using mock for demo, swap for real API key
    results = {}

    for problem in problems:
        problem_results = []
        for iterations in iterations_list:
            start_time = time.time()
            engine = MCTSEngine(client, problem['desc'], problem['test'], starting_code=problem['seed'])
            final_code = engine.run(iterations=iterations)
            duration = time.time() - start_time
            
            # Simple success check for demo
            success = "return" in final_code and "def" in final_code
            problem_results.append({
                "iterations": iterations,
                "success": success,
                "time": duration
            })
        results[problem['name']] = problem_results

    plot_results(results, iterations_list)

def plot_results(results, iterations_list):
    plt.figure(figsize=(10, 6))
    for name, data in results.items():
        success_rates = [1 if d['success'] else 0 for d in data]
        plt.plot(iterations_list, success_rates, marker='o', label=name)

    plt.title("MCTS Performance: Success vs. Iterations")
    plt.xlabel("Iterations")
    plt.ylabel("Success (Binary)")
    plt.legend()
    plt.grid(True)
    plt.savefig("benchmarks/performance_graph.png")
    print("Graph saved to benchmarks/performance_graph.png")

if __name__ == "__main__":
    test_problems = [
        {
            "name": "Factorial",
            "desc": "Calculate factorial of n",
            "seed": "def factorial(n):",
            "test": "assert factorial(5) == 120"
        },
        {
            "name": "Fibonacci",
            "desc": "Return nth fibonacci number",
            "seed": "def fibonacci(n):",
            "test": "assert fibonacci(5) == 5"
        }
    ]
    run_benchmark(test_problems)
