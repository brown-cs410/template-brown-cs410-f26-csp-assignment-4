from dataclasses import dataclass, field
from typing import List, Optional

from sat_problem import Model


@dataclass
class SearchStats:
    """
    Runtime statistics collected while a SATAlgorithm searches for a model
    that satisfies a CNF formula.

    Attributes:
        num_iterations: Number of variable flips performed.
        num_unsatisfied_clauses: Number of unsatisfied clauses recorded after
            each flip (used to plot search progress).
        runtime_seconds: Total runtime of the search in seconds.
    """

    num_iterations: int = 0
    num_unsatisfied_clauses: List[int] = field(default_factory=list)
    runtime_seconds: float = 0.0


class SATSolution:
    """
    The result of running a SATAlgorithm on a CNF formula.

    A SATAlgorithm always returns one of these, even when no satisfying
    model is found -- in that case `model` is None.
    """

    def __init__(self, model: Optional[Model] = None) -> None:
        self.model: Optional[Model] = model
        self.stats: SearchStats = SearchStats()

    def __repr__(self) -> str:
        return (
            f"SATSolution(found={self.model is not None}, "
            f"num_iterations={self.stats.num_iterations}, "
            f"runtime_seconds={self.stats.runtime_seconds:.4f})"
        )
