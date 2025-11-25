import random
from typing import Optional, Callable
from src.mcts.node import MCTSNode
from src.environment.sandbox import CodeSandbox
from src.llm.abstract_client import AbstractLLMClient
from src.utils.logger import logger

class MCTSEngine:
    """
    The orchestrator implementing the Monte Carlo Tree Search algorithm.
    """
    def __init__(self, llm_client: AbstractLLMClient, problem_desc: str, test_harness: str, starting_code: str = ""):
        self.llm = llm_client
        self.problem = problem_desc
        self.test_harness = test_harness
        self.sandbox = CodeSandbox()
        self.root = MCTSNode(state=starting_code) 

    # UPDATE: Added 'on_step' callback parameter
    def run(self, iterations: int = 10, on_step: Callable[[str], None] = None) -> str:
        
        log_msg = f"Starting MCTS Search for {iterations} iterations..."
        logger.info(log_msg)
        if on_step: on_step(log_msg)
        
        for i in range(iterations):
            # 1. Selection
            node = self._select(self.root)
            
            # 2. Expansion
            if not node.is_terminal:
                if node.visits > 0:
                    node = self._expand(node)
            
            # 3. Simulation
            reward = self._simulate(node)
            
            # 4. Backpropagation
            self._backpropagate(node, reward)
            
            # Logging & UI Update
            depth = self._get_depth(node)
            snippet = node.state.replace("\n", " ")[-40:]
            
            status = "SyntaxErr" if reward == -1.0 else "Valid/Inc"
            
            if reward == 1.0:
                success_msg = f"ITER {i+1}: 🌟 SOLUTION FOUND at depth {depth}"
                logger.info(success_msg)
                if on_step: on_step(success_msg)
                return node.state
            else:
                step_msg = f"ITER {i+1}: Depth {depth} | Reward: {reward} ({status}) | ...{snippet}"
                logger.info(step_msg)
                if on_step: on_step(step_msg)

        best_node = self._get_best_child(self.root)
        logger.warning("Max iterations reached.")
        return best_node.state

    def _select(self, node: MCTSNode) -> MCTSNode:
        while node.children and node.is_fully_expanded:
            node = node.best_child()
        return node

    def _expand(self, node: MCTSNode) -> MCTSNode:
        candidates = self.llm.generate_candidates(self.problem, node.state, n=3)
        for code_snippet in candidates:
            separator = "\n" 
            if node.state.endswith("\n") or code_snippet.startswith("\n"):
                separator = ""
            new_state = f"{node.state}{separator}{code_snippet}"
            child = MCTSNode(state=new_state, parent=node)
            node.children.append(child)
        
        node.is_fully_expanded = True
        return random.choice(node.children)

    def _simulate(self, node: MCTSNode) -> float:
        result = self.sandbox.execute(node.state, self.test_harness)
        
        if result['success']:
            node.is_terminal = True
            return 1.0
        elif result['error_type'] == 'syntax':
            return -1.0 
        else:
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