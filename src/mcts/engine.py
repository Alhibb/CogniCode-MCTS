import random
from typing import Optional
from src.mcts.node import MCTSNode
from src.environment.sandbox import CodeSandbox
from src.llm.abstract_client import AbstractLLMClient
from src.utils.logger import logger

class MCTSEngine:
    def __init__(self, llm_client: AbstractLLMClient, problem_desc: str, test_harness: str, starting_code: str = ""):
        self.llm = llm_client
        self.problem = problem_desc
        self.test_harness = test_harness
        self.sandbox = CodeSandbox()
        self.root = MCTSNode(state=starting_code) 

    def run(self, iterations: int = 10) -> str:
        logger.info(f"Starting MCTS Search for {iterations} iterations...")
        
        for i in range(iterations):
            node = self._select(self.root)
            
            if not node.is_terminal:
                if node.visits > 0:
                    node = self._expand(node)
            
            reward = self._simulate(node)
            self._backpropagate(node, reward)
            
            depth = self._get_depth(node)
            snippet = node.state.replace("\n", " ")[-40:]
            
            if reward == 1.0:
                logger.info(f"ITER {i+1}: 🌟 SOLUTION FOUND at depth {depth}")
                return node.state
            else:
                # Cleaner logging
                status = "SyntaxErr" if reward == -1.0 else "Valid/Inc"
                logger.info(f"ITER {i+1}: D{depth} | R:{reward} ({status}) | ...{snippet}")

        best_node = self._get_best_child(self.root)
        logger.warning("Max iterations reached. Returning best partial solution.")
        return best_node.state

    def _select(self, node: MCTSNode) -> MCTSNode:
        while node.children and node.is_fully_expanded:
            node = node.best_child()
        return node

    def _expand(self, node: MCTSNode) -> MCTSNode:
        candidates = self.llm.generate_candidates(self.problem, node.state, n=3)
        for code_snippet in candidates:
            # Clean newline handling
            # If the snippet starts with a newline, don't add another
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
            # Code is syntactically valid (or incomplete but valid structure)
            # Give small reward to encourage depth
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