import argparse
import os
import random
from typing import List, Dict, Tuple, Optional, Any

import examples
import numpy as np
from sat_problem import CNF, Clause, Literal, Model, Variable
from sat_solvers import GSAT, WalkSAT
from vizualize import print_sudoku, visualize_sudoku
from search_problem import SearchProblem

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

class Sudoku(SearchProblem):
    """
    A class representing a Sudoku problem, which compiles to a CNF formula.
    
    Supports different sized Sudoku problems (4x4, 9x9, 16x16, etc.)
    by encoding the standard Sudoku constraints as logical clauses.
    """

    def __init__(self, starting_grid: Optional[List[List[int]]] = None) -> None:
        """
        Initialize a Sudoku problem with the given starting configuration.
        
        Args:
            starting_grid: 2D list representing the initial Sudoku state.
                          0 represents empty cells. Defaults to empty 4x4 grid.
        """
        if starting_grid is None:
            starting_grid = [[0]*4]*4
        self.starting_grid = starting_grid
        self.size = len(self.starting_grid)
        self.subgrid_size = int(np.sqrt(self.size))

    def compile(self) -> CNF:
        """
        Build a CNF formula encoding the Sudoku constraints.

        Returns:
            A CNF formula whose satisfying models are valid Sudoku solutions.
        """
        cnf = CNF()

        # cache for Variables
        variable_cache: Dict[Tuple[int, int, int], Variable] = {}

        def get_variable(row: int, col: int, num: int) -> Variable:
            key = (row, col, num)
            if key not in variable_cache:
                variable_cache[key] = Variable(f'x_{row}_{col}_{num}')
            return variable_cache[key]

        # TODO: Implement the constraints for Sudoku, TASK 2
        # Add each constraint to `cnf` using cnf.add_clause(...)

        return cnf

    def get_board(self, solution: Model) -> List[List[int]]:
        """
        Convert a solution model to a Sudoku board representation.

        Args:
            solution: Model containing variable assignments for the solved Sudoku
            
        Returns:
            2D list representing the completed Sudoku board with numbers 1-N
        """
        assignment = solution.assignment
        solution_grid = [[0] * self.size for _ in range(self.size)]

        for var, value in assignment.items():
            if value == 1:
                _, row, col, num = str(var).split('_')
                row = int(row)
                col = int(col)
                num = int(num)

                solution_grid[row][col] = num

        return solution_grid


def main() -> None:
    """
    Main function to solve Sudoku puzzles using SAT solvers.
    
    Parses command line arguments and runs either GSAT or WalkSAT
    on a Sudoku puzzle of specified difficulty.
    """
    parser = argparse.ArgumentParser(
        description="Solve the N-Queens problem using a SAT solver.")
    parser.add_argument("-p", type=float, default=0.5,
                        help="Probability parameter for GSAT/WalkSAT (default: 0.5)")
    parser.add_argument("--randomized_restarts", type=int, default=1,
                        help="Number of randomized restarts to run (default: 1)")
    parser.add_argument("--max_iterations", type=int, default=10000,
                        help="Maximum number of iterations (default: 10000)")
    parser.add_argument("--solver", type=str, default="walksat",
                        help="Solver to use (walksat or gsat)")
    parser.add_argument("--difficulty", type=str, default="medium",
                        help="Difficulty level of the Sudoku puzzle (easy, medium, hard)")
    args = parser.parse_args()

    # Try on empty 9x9 grid
    example_start_grids = examples.get_sudoku_puzzles()
    starting_grid = example_start_grids[args.difficulty][0]
    problem = Sudoku(starting_grid)
    cnf = problem.compile()

    if args.solver == "gsat":
        print("Running GSAT...")
        result = GSAT(max_iterations=args.max_iterations, p=args.p,
                      num_randomized_restarts=args.randomized_restarts).satisfy(cnf)
        if result.model is not None:
            print("Solution found!")
            board = problem.get_board(result.model)
            print("Runtime:", result.stats.runtime_seconds)
            print_sudoku(board)
        else:
            print("No solution found.")

    elif args.solver == "walksat":
        print("Running WalkSAT...")
        result = WalkSAT(max_iterations=args.max_iterations, p=args.p,
                         num_randomized_restarts=args.randomized_restarts).satisfy(cnf)
        if result.model is not None:
            print("Solution found!")
            board = problem.get_board(result.model)
            print_sudoku(board)
            print("Runtime:", result.stats.runtime_seconds)
            visualize_sudoku(board)
        else:
            print("No solution found.")

if __name__ == "__main__":
    random.seed(42)
    main()