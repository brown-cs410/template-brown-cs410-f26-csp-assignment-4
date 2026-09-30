import unittest
from typing import Optional

from sat_solvers import GSAT, WalkSAT
from sat_problem import Clause, Literal, Variable, CNF, Model


class IOTest(unittest.TestCase):
    """
    Tests input/output for SAT solver implementations.

    Contains basic test cases to verify that GSAT
    correctly solves simple CNF formulas and makes optimal decisions.
    """

    def test_basic_cnf_gsat(self) -> None:
        """
        Test if GSAT can solve a basic CNF formula.

        Tests GSAT's ability to find a satisfying assignment for a simple
        CNF formula starting from a partially unsatisfying initial state.

        CNF = (A or B) and (~B or C) and (B or ~A) and (B or D)
        Example solution: A=True, B=True, C=True, D=True
        """
        cnf = CNF()
        cnf.add_clause(
            Clause([Literal(Variable("A"), True), Literal(Variable("B"), True)]))
        cnf.add_clause(
            Clause([Literal(Variable("B"), False), Literal(Variable("C"), True)]))
        cnf.add_clause(
            Clause([Literal(Variable("B"), True), Literal(Variable("A"), False)]))
        cnf.add_clause(
            Clause([Literal(Variable("B"), False), Literal(Variable("D"), True)]))
        cnf_model = Model(cnf)
        cnf_model.assign(Variable("A"), False)
        cnf_model.assign(Variable("B"), False)
        cnf_model.assign(Variable("C"), True)
        cnf_model.assign(Variable("D"), False)
        result = GSAT(max_iterations=500, p=0,
                      existing_model=cnf_model).satisfy(cnf)
        self.assertIsNotNone(result.model, "The solver should return a solution model")
        model = result.model
        assert(model)
        A = model.assignment[Variable("A")]
        B = model.assignment[Variable("B")]
        C = model.assignment[Variable("C")]
        D = model.assignment[Variable("D")]

        self.assertTrue((A or B) and (not B or C)
                        and (B or not A) and (B or D))
        print('GSAT solves a simple CNF!')


if __name__ == "__main__":
    unittest.main()
