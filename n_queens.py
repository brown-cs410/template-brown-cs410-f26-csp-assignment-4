from typing import List, Optional, Dict, Union
from sat_solvers import GSAT, WalkSAT
from sat_problem import CNF, Variable, Clause, Literal, Model
from vizualize import visualize_n_queens, print_n_queens
import random
import argparse
from search_problem import SearchProblem

class NQueens(SearchProblem):
    """
    A class representing the N-Queens problem, which compiles to a CNF formula.
    
    The N-Queens problem involves placing N queens on an N×N chessboard
    such that no two queens attack each other (no two queens share the same
    row, column, or diagonal).
    """

    def __init__(self, size: int = 8) -> None:
        """
        Initialize the N-Queens problem with the given board size.
        
        Args:
            size: The size of the chessboard (number of queens to place)
        """
        self.size = size

    def compile(self) -> CNF:
        """
        Build a CNF formula encoding the N-Queens constraints.

        Returns:
            A CNF formula whose satisfying models are valid queen placements.

        Generates clauses ensuring:
        1. Exactly one queen per row
        2. Exactly one queen per column  
        3. At most one queen per diagonal (both directions)
        """
        cnf = CNF()

        variable_cache: Dict[tuple, Variable] = {}
        
        def get_variable(row: int, col: int) -> Variable:
            key = (row, col)
            if key not in variable_cache:
                variable_cache[key] = Variable(f'x_{row}_{col}')
            return variable_cache[key]

        # each row must have exactly one queen
        for i in range(self.size):
            # at least one queen in each row
            clause = Clause([Literal(get_variable(i, j), True)
                            for j in range(self.size)])
            cnf.add_clause(clause)
            # at most one queen in each row
            for j in range(self.size):
                for k in range(j + 1, self.size):
                    clause = Clause(
                        [Literal(get_variable(i, j), False), Literal(get_variable(i, k), False)])
                    cnf.add_clause(clause)

        # each column must have exactly one queen
        for j in range(self.size):
            # at least one queen in each column
            clause = Clause([Literal(get_variable(i, j), True)
                            for i in range(self.size)])
            cnf.add_clause(clause)
            # at most one queen in each column
            for i in range(self.size):
                for k in range(i + 1, self.size):
                    clause = Clause(
                        [Literal(get_variable(i, j), False), Literal(get_variable(k, j), False)])
                    cnf.add_clause(clause)

        # \ diagonal constraints
        for d in range(2 * self.size - 1):
            literals = []
            for i in range(self.size):
                j = d - i
                if 0 <= j < self.size:
                    literals.append(Literal(get_variable(i, j), True))
            for p in range(len(literals)):
                for q in range(p + 1, len(literals)):
                    clause = Clause(
                        [Literal(literals[p].variable, False), Literal(literals[q].variable, False)])
                    cnf.add_clause(clause)

        # / diagonal constraints
        for d in range(2 * self.size - 1):
            literals = []
            for i in range(self.size):
                j = i - d + self.size - 1
                if 0 <= j < self.size:
                    literals.append(Literal(get_variable(i, j), True))
            for p in range(len(literals)):
                for q in range(p + 1, len(literals)):
                    clause = Clause(
                        [Literal(literals[p].variable, False), Literal(literals[q].variable, False)])
                    cnf.add_clause(clause)

        return cnf

    def get_board(self, solution: Optional[Model]) -> Union[str, List[List[str]]]:
        """
        Convert a solution model to a visual board representation.
        
        Args:
            solution: The model containing variable assignments (or None if no solution)
            
        Returns:
            Either a string indicating no solution found, or a 2D list representing
            the board with 'Q' for queens and '.' for empty squares
        """
        if solution is None:
            return "No solution found."

        board = [['.' for _ in range(self.size)] for _ in range(self.size)]
        for var, value in solution.assignment.items():
            if value == 1:
                _, row, col = str(var).split('_')
                row = int(row)
                col = int(col)
                board[row][col] = 'Q'

        return board


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Solve the N-Queens problem using a SAT solver.")
    parser.add_argument("-n", type=int, default=8,
                        help="Size of the board (default: 8)")
    parser.add_argument("-p", type=float, default=0.5,
                        help="Probability parameter for GSAT/WalkSAT (default: 0.5)")
    parser.add_argument("--randomized_restarts", type=int, default=1,
                        help="Number of randomized restarts to run (default: 1)")
    parser.add_argument("--max_iterations", type=int, default=10000,
                        help="Maximum number of iterations (default: 10000)")
    args = parser.parse_args()
    random.seed(42)
    problem = NQueens(args.n)
    cnf = problem.compile()

    print("Starting to solve w/ GSAT")
    result = GSAT(
        max_iterations=args.max_iterations, p=args.p,
        num_randomized_restarts=args.randomized_restarts).satisfy(cnf)
    print("GSAT Solution:")
    board = problem.get_board(result.model)
    print_n_queens(board)

    print("Starting to solve w/ WalkSAT")
    result = WalkSAT(
        max_iterations=args.max_iterations, p=args.p,
        num_randomized_restarts=args.randomized_restarts).satisfy(cnf)
    print("WalkSAT Solution:")
    board = problem.get_board(result.model)
    print_n_queens(board)

    if result.model is not None:
        board = problem.get_board(result.model)
        visualize_n_queens(board)
        print("iterations:", result.stats.num_iterations,
              "Runtime:", result.stats.runtime_seconds)
    else:
        print("No solution found.")
