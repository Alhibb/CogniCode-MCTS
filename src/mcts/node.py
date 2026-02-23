import math
from typing import List, Optional

class MCTSNode:
    """
    Represents a state in the code generation tree.
    """
    def __init__(self, state: str, parent: Optional['MCTSNode'] = None, prior: float = 0.0):
        self.state = state  
        self.parent = parent
        self.children: List['MCTSNode'] = []
        self.visits: int = 0
        self.value: float = 0.0 
        self.prior: float = prior # Prior probability from LLM
        self.is_terminal: bool = False
        self.is_fully_expanded: bool = False

    def puct(self, c_puct: float = 1.41) -> float:
        """
        Calculates PUCT (Predictor + UCB for Trees).
        """
        # exploitation = Q-value
        exploitation = self.value / self.visits if self.visits > 0 else 0
        
        # exploration = Prior * sqrt(parent_visits) / (1 + visits)
        parent_visits = self.parent.visits if self.parent else 1
        exploration = c_puct * self.prior * (math.sqrt(parent_visits) / (1 + self.visits))
        
        return exploitation + exploration

    def ucb1(self, exploration_weight: float = 1.41) -> float:
        """
        Calculates Upper Confidence Bound.
        """
        if self.visits == 0:
            return float('inf')
        
        # Avoid division by zero for parent visits in root case
        parent_visits = self.parent.visits if self.parent else 1
        if parent_visits == 0:
            parent_visits = 1

        exploitation = self.value / self.visits
        exploration = exploration_weight * math.sqrt(math.log(parent_visits) / self.visits)
        return exploitation + exploration

    def best_child(self, use_puct: bool = True) -> Optional['MCTSNode']:
        if not self.children:
            return None
        if use_puct:
            return max(self.children, key=lambda c: c.puct())
        return max(self.children, key=lambda c: c.ucb1())

    def __repr__(self):
        return f"<Node visits={self.visits} val={self.value:.2f} len={len(self.state)}>"
