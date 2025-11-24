import random
from typing import Optional
from src.mcts.node import MCTSNode
from src.environment.sandbox import CodeSandbox
from src.llm.abstract_client import AbstractLLMClient
from src.utils.logger import logger

class MCTSEngine:
    """
    The orchestrator implementing the Monte Carlo Tree Search algorithm.
    """
    def __init__(self, llm_client: AbstractLLMClient, problem_desc: str, test_harness: str):
        self.llm = llm_client
        self.problem = problem_desc
        self.test_harness = test_harness
        self.sandbox = CodeSandbox()
        # The root state usually contains imports or the function header
        self.root = MCTSNode(state="") 

    def run(self, iterations: int = 10) -> str:
        logger.info(f"Starting MCTS Search for {iterations} iterations...")
        
        for i in range(iterations):
            # 1. Selection
            node = self._select(self.root)
            
            # 2. Expansion
            # If the node isn't a terminal state (success), expand it
            if not node.is_terminal:
                if node.visits > 0:
                    node = self._expand(node)
                # If visits == 0, we simulate the node itself (Rollout)
            
            # 3. Simulation
            reward = self._simulate(node)
            
            # 4. Backpropagation
            self._backpropagate(node, reward)
            
            # Logging for visualization
            if reward == 1.0:
                logger.info(f"ITER {i+1}: 🌟 SOLUTION FOUND at depth {self._get_depth(node)}")
                return node.state
            else:
                logger.info(f"ITER {i+1}: Visited depth {self._get_depth(node)} | Reward: {reward}")

        # Fallback: Return best visited path
        best_node = self._get_best_child(self.root)
        logger.warning("Max iterations reached. Returning best partial solution.")
        return best_node.state

    def _select(self, node: MCTSNode) -> MCTSNode:
        """Traverse down the tree using UCB1 until a leaf or unexpanded node is found."""
        while node.children and node.is_fully_expanded:
            node = node.best_child()
        return node

    def _expand(self, node: MCTSNode) -> MCTSNode:
        """Ask LLM for N variations of the next step."""
        candidates = self.llm.generate_candidates(self.problem, node.state, n=3)
        
        for code_snippet in candidates:
            # Combine previous state with new snippet
            new_state = f"{node.state}\n{code_snippet}".strip()
            child = MCTSNode(state=new_state, parent=node)
            node.children.append(child)
        
        node.is_fully_expanded = True
        
        # Return a random child to start simulation
        return random.choice(node.children)

    def _simulate(self, node: MCTSNode) -> float:
        """Run the code in the sandbox."""
        result = self.sandbox.execute(node.state, self.test_harness)
        
        if result['success']:
            node.is_terminal = True
            return 1.0
        elif result['error_type'] == 'syntax':
            return -1.0 # Heavy penalty for invalid syntax
        else:
            # Code runs but fails logic. 
            # In a full version, we would use LLM heuristic here.
            # For now, small reward for runnable code.
            return 0.1

    def _backpropagate(self, node: Optional[MCTSNode], reward: float):
        while node:
            node.visits += 1
            node.value += reward
            node = node.parent

    def _get_best_child(self, node: MCTSNode) -> MCTSNode:
        if not node.children: return node
        return max(node.children, key=lambda c: c.visits)

    def _get_depth(self, node: MCTSNode) -> int:
        depth = 0
        curr = node
        while curr.parent:
            depth += 1
            curr = curr.parent
        return depth