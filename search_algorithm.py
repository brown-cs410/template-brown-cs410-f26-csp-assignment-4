from abc import ABC, abstractmethod
from typing import Optional

from sat_problem import CNF, Model
from search_solution import SATSolution


class SATAlgorithm(ABC):
    """
    A SATAlgorithm searches for an Model that satisfies a CNF formula and
    returns a SATSolution containing that model (or None, if no satisfying
    model was found) and statistics about the search.
    """

    name: str = ""

    def __init__(
        self,
        max_iterations: int = 10000,
        num_randomized_restarts: int = 1,
        existing_model: Optional[Model] = None,
    ) -> None:
        """
        Args:
            max_iterations: Maximum number of variable flips to perform per restart
            num_randomized_restarts: Number of random restarts to attempt
            existing_model: Optional starting model (used primarily for testing).
                If provided, search starts from this model instead of a random
                assignment.
        """
        self.max_iterations = max_iterations
        self.num_randomized_restarts = num_randomized_restarts
        self.existing_model = existing_model

    @abstractmethod
    def satisfy(self, CNF_formula: CNF) -> SATSolution:
        """
        Search for a model that satisfies the given CNF formula.

        Args:
            CNF_formula: The CNF formula to satisfy.

        Returns:
            A SATSolution containing the satisfying Model (or None) and
            search statistics.
        """
        pass
