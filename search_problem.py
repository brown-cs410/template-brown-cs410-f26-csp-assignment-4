from abc import ABC, abstractmethod
from typing import Any, Optional
from sat_problem import CNF, Model


class SearchProblem(ABC):
    """
    A problem (e.g., N-Queens or Sudoku) that can be compiled into a CNF
    formula and solved by a SATAlgorithm.
    """

    @abstractmethod
    def compile(self) -> CNF:
        """
        Compile the problem into a CNF formula encoding its constraints.

        Returns:
            A CNF formula whose satisfying models are solutions to the problem.
        """
        pass

    @abstractmethod
    def get_board(self, solution: Optional[Model]) -> Any:
        """
        Convert a solution Model into a board representation.

        Args:
            solution: A satisfying Model, or None if no solution was found.

        Returns:
            A representation of the solved board.
        """
        pass
