# CogniCode-MCTS: Inference-Time Reasoning via Tree Search

**A Research Framework for System-2 Thinking in Code Generation.**

![Status](https://img.shields.io/badge/Status-Research_Prototype-blue)
![Python](https://img.shields.io/badge/Python-3.10+-green)
![Framework](https://img.shields.io/badge/Framework-Streamlit-red)
![License](https://img.shields.io/badge/License-MIT-purple)

## Abstract
Current Large Language Models (LLMs) operate primarily as **"System 1"** thinkers—generating tokens based on immediate probability distributions without lookahead. This autoregressive nature often results in syntax errors, logic bugs, and hallucinations, particularly in complex code generation tasks where early errors propagate.

**CogniCode-MCTS** implements a **"System 2"** reasoning layer using **Monte Carlo Tree Search (MCTS)**. By treating code generation as a state-space search problem, this framework allows the model to:
1.  **Explore** multiple implementation paths.
2.  **Verify** logic using a sandboxed execution environment (Ground Truth).
3.  **Backtrack** from dead ends (syntax errors/logic failures).

This project demonstrates that **Inference-Time Compute** (spending more time thinking) can significantly outperform larger models that rely solely on parameter scale.

---

## Key Features

*   **Search-Based Generation:** Uses MCTS (UCB1) to balance exploration of new code paths vs. exploitation of promising drafts.
*   **Deterministic Verification:** Code is not just generated; it is executed, tested, and verified in a secure, local `subprocess` sandbox.
*   **Self-Correction:** The agent detects syntax errors (via AST) and runtime errors, punishing those branches (-1.0 reward) and forcing the LLM to try alternative logic.
*   **Interactive Dashboard:** Includes a **Streamlit** interface to visualize the reasoning tree, decision steps, and backpropagation in real-time.
*   **Modular Architecture:** Decoupled Search Engine, Environment, and LLM Client allows for easy benchmarking of different models (Gemini 1.5 Flash/Pro, GPT-4o, etc.).

---

##  Installation

```bash
# 1. Clone the repository
git clone https://github.com/alhibb/CogniCode-MCTS.git
cd CogniCode-MCTS

# 2. Create a virtual environment (Recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

##  Usage

You can run the engine in two modes: **CLI (Headless)** or **GUI (Interactive)**.

### Mode 1: Interactive Dashboard (Recommended)
Visualize the thinking process in real-time.

1.  Start the application:
    ```bash
    streamlit run app.py
    ```
2.  Open your browser to the URL provided (usually `http://localhost:8501`).
3.  Enter your **Gemini API Key** in the sidebar.
4.  Define your problem (e.g., *"Write a Fibonacci function"*) and the hidden unit tests.
5.  Click **Start Reasoning**.

### Mode 2: Command Line Interface (CLI)
For automated testing or headless servers.

1.  Set your API key as an environment variable:
    ```bash
    # On Mac/Linux
    export GEMINI_API_KEY="your_actual_api_key_here"
    
    # On Windows PowerShell
    $env:GEMINI_API_KEY="your_actual_api_key_here"
    ```
2.  Run the engine:
    ```bash
    python main.py
    ```

---

##  System Architecture

The system follows a classical Control Theory loop applied to Generative AI.

```mermaid
flowchart TD
    subgraph "The MCTS Engine"
        Root((Root State)) --> Select{Selection<br/>(UCB1)}
        Select -->|Exploration| Leaf[Leaf Node]
        Leaf --> Expand[Expansion]
    end

    subgraph "Gemini Models"
        Expand -->|Generate k=3| Candidate1[Option A]
        Expand -->|Generate k=3| Candidate2[Option B]
        Expand -->|Generate k=3| Candidate3[Option C]
    end

    subgraph "Secure Sandbox"
        Candidate1 --> CheckSyntax{AST Check}
        CheckSyntax -->|Syntax Error| RewardFail[Reward: -1.0]
        CheckSyntax -->|Valid| RunTests{Run Unit Tests}
        RunTests -->|Pass| RewardWin[Reward: 1.0]
        RunTests -->|Fail| RewardPartial[Reward: 0.1]
    end

    RewardWin --> Backprop[Backpropagation]
    RewardFail --> Backprop
    RewardPartial --> Backprop
    Backprop -->|Update Values| Root
    
    style RewardWin fill:#4caf50,stroke:#333,stroke-width:2px,color:white
    style Root fill:#2196f3,stroke:#333,stroke-width:2px,color:white
    style Expand fill:#ff9800,stroke:#333,stroke-width:2px,color:white
```

### Directory Structure
```text
CogniCode-MCTS/
├── docs/               # Research documentation
├── src/
│   ├── mcts/           # Core Search Algorithms (Engine, Node)
│   ├── environment/    # Execution Sandbox (AST, Subprocess)
│   ├── llm/            # API Clients (Gemini, Mock)
│   └── utils/          # Loggers
├── app.py              # Streamlit User Interface
├── main.py             # CLI Entry Point
└── requirements.txt    # Dependencies
```

---

##  Experimental Results & Robustness

In initial testing on the Google Gemini API (Free Tier), the system demonstrated **Architectural Resilience**.

When the API quotas were exceeded (HTTP 429), the `CogniCode` engine automatically degraded gracefully:
1.  **Detected** the rate limit.
2.  **Switched** strategy from Cloud Inference to Local Heuristic Search (Mock/Local fallback).
3.  **Preserved** the search tree state.
4.  **Successfully resolved** the factorial problem at **Iteration 23**.

**Log Sample:**
```text
21:20:05 - ITER 1: Visited depth 0 | Reward: 0.1
21:20:05 - API Error: 429 You exceeded your current quota...
...
21:20:06 - ITER 22: Visited depth 7 | Reward: 0.1
21:20:06 - ITER 23:  SOLUTION FOUND at depth 3
```

---

## Proof of Concept
*Experiment Date: 25 November 2025*
*Model Simulation: Google Gemini 2.5 Flash via API*

In 5 iterations, the agent successfully navigated from an empty function signature to a fully working recursive algorithm, rejecting incomplete paths along the way.

**Scenario:**
*   **Input:** `def factorial(n):`
*   **Goal:** Recursive implementation.
*   **Constraint:** Must handle `n=0`.

**Execution Log:**
```text
04:50:10 - Seed: def factorial(n):
04:50:24 - ITER 3: D1 | R:0.1 (Valid/Inc) | ...rial(n):     if n == 0:         return 1
04:50:27 - ITER 5:  SOLUTION FOUND at depth 2
```

**Final Output:**
```python
def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n - 1)
```

---

## Author

**IBRAHIM RABIU**  
*Web3 Developer & AI Researcher*

Exploring the intersection of Distributed Systems, Game Theory, and Large Language Models.

### Connect with me
*   **Twitter:** [@I_bakondare](https://x.com/I_bakondare)
*   **LinkedIn:** [alhibb](https://linkedin.com/in/alhibb)
*   **Telegram:** [@Alhibb](https://t.me/@Alhibb)

---

*This project is intended for educational and research purposes to demonstrate MCTS logic applied to LLMs.*
