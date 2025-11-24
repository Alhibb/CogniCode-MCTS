from abc import ABC, abstractmethod
from typing import List

class AbstractLLMClient(ABC):
    @abstractmethod
    def generate_candidates(self, problem: str, current_state: str, n: int = 3) -> List[str]:
        """
        Generates 'n' possible continuations for the code.
        """
        pass
