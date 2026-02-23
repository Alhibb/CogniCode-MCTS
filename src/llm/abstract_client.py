from abc import ABC, abstractmethod
from typing import List

class AbstractLLMClient(ABC):
    @abstractmethod
    def generate_candidates(self, problem: str, current_state: str, n: int = 3) -> List[str]:
        """
        Generates 'n' possible continuations for the code.
        """
        pass

    @abstractmethod
    def predict_value(self, problem: str, current_state: str) -> float:
        """
        Predicts the value (probability of success) of the current state.
        Returns a float between 0.0 and 1.0.
        """
        pass
