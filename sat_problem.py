from typing import List, Set, Dict, Optional, Tuple
from collections import defaultdict

class Variable:
    """
    A class to represent a variable in a CNF formula.
    A variable is the smallest building block in SAT formulas.
    This class contains useful methods for working with variables, 
    including methods for printing, checking equality,
    and hashing (for use in dictionaries).

    Attributes:
        name (str): The name of the variable.
    """

    def __init__(self, name: str) -> None:
        self.name = name

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Variable):
            return False
        return self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)


class Literal:
    """
    A class to represent a literal in a CNF formula.
    A literal is a variable with a flag indicating whether it is negated or not.
    This class contains methods for checking if two literals are equal and a hash function (for use in dictionaries).

    Attributes:
        variable (Variable): The variable associated with the literal.
        is_positive (bool): A boolean indicating whether the literal is positive or negated.
    """

    def __init__(self, variable: Variable, is_positive: bool) -> None:
        self.variable = variable
        self.is_positive = is_positive

    def __str__(self) -> str:
        return f"{'~' if not self.is_positive else ''}{self.variable}"

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Literal):
            return False
        return self.variable == other.variable and self.is_positive == other.is_positive

    def __hash__(self) -> int:
        return hash((self.variable, self.is_positive))


class Clause:
    """
    A class to represent a clause in a CNF formula.
    Note: a clause is assumed to be a disjunction of literals.

    Attributes:
        literals (list): A list of literals in the clause.
        variables_set (set): A set of variables in the clause.
    """

    def __init__(self, literals: List[Literal]) -> None:
        self.literals: List[Literal] = list(literals)
        self.variables_set: Set[Variable] = {
            literal.variable for literal in literals}
        # hash is computed once, from a frozenset so literal order doesn't matter,
        # since clauses are used as keys in dictionaries and sets.
        self._hash = hash(frozenset(self.literals))

    def __str__(self) -> str:
        return "(" + " Or ".join(map(str, self.literals)) + ")"

    def __repr__(self) -> str:
        return str(self)

    def __hash__(self) -> int:
        return self._hash

    def get_variables(self) -> List[Variable]:
        """
        Get list of variables in clause

        Returns:
            List of variables in the clause
        """
        return list(self.variables_set)


class CNF:
    """
    A class to represent a CNF formula. A CNF formula is a conjunction of disjunctive clauses 
    (i.e., clauses with only ORs that are ANDed together).
    CNF formulae should be constructed using the add_clause method to add clauses (do not manually add to clauses list).

    Attributes:
        clauses (list): A list of clauses in the CNF formula.
        variables (dict): A dictionary mapping variables to the clauses they appear in.
        literal_clause_map (dict): A dictionary mapping literals to the clauses they appear in.
    """

    def __init__(self, clauses: Optional[List[Clause]] = None) -> None:
        self.clauses: List[Clause] = list(clauses) if clauses else []
        self.variables: Dict[Variable, Set[Clause]] = defaultdict(set)
        self.literal_clause_map: Dict[Literal, Set[Clause]] = defaultdict(set)

        for clause in self.clauses:
            for literal in clause.literals:
                self.variables[literal.variable].add(clause)
                self.literal_clause_map[literal].add(clause)

    def add_clause(self, clause: Clause) -> None:
        """
        Add clause to CNF and update appropriate attributes.

        Args:
            clause: The clause to add to the CNF
        """
        self.clauses.append(clause)
        for literal in clause.literals:
            self.variables[literal.variable].add(clause)
            self.literal_clause_map[literal].add(clause)

    def __str__(self) -> str:
        return " And ".join(map(str, self.clauses))


class Model:
    """
    A class to represent a literal assignment for a CNF formula.
    Contains methods for checking if a literal assignment satisfies a CNF formula,
    and methods for updating the assignment when a variable is assigned or "flipped".

    Attributes:
        CNF (CNF): The CNF formula that the literal assignment is for.
        variables (list): A list of variables in the CNF formula.
        assignment (dict): A dictionary mapping variables to their assigned values
            (1 for True, 0 for False, -1 for unassigned).
        satisfied_literals (dict): A dictionary mapping clauses to the literals that satisfy them. (for internal use)
        unsatisfied_clauses (set): A set of clauses that are not satisfied by the current literal assignment.
        flipped (list): A list of every variable that has been flipped, in order (for internal use and testing).
    """

    def __init__(self, CNF: CNF) -> None:
        self.CNF = CNF
        self.variables: List[Variable] = list(CNF.variables.keys())
        self.assignment: Dict[Variable, int] = {v: -1 for v in CNF.variables.keys()}
        self.satisfied_literals: Dict[Clause, Set[Literal]] = defaultdict(set)
        self.unsatisfied_clauses: Set[Clause] = set(CNF.clauses)
        self.flipped: List[Variable] = []


    def assign(self, variable: Variable, value: bool) -> None:
        """
        Assign a value to a variable in the model.
        
        Updates satisfied clauses in Model based on the new assignment.

        Args:
            variable: The variable to assign a value to
            value: The boolean value to assign to the variable
        """
        old_value = self.assignment[variable]
        self.assignment[variable] = int(value)
        self.update_clause_satisfaction(variable, old_value, int(value))

    def flip(self, variable: Variable) -> None:
        """
        Flip a variable (from True to False or from False to True).
        
        Updates satisfied clauses in Model based on the flipped assignment.

        Args:
            variable: The variable to flip
        """
        old_value = self.assignment[variable]
        new_value = 1 - old_value if old_value != -1 else 1
        self.assignment[variable] = new_value
        self.flipped.append(variable)
        self.update_clause_satisfaction(variable, old_value, new_value)

    def update_clause_satisfaction(self, variable: Variable, old_value: int, new_value: int) -> None:
        """
        Update satisfied and unsatisfied clauses after variable assignment.
        
        This approach of tracking satisfied clauses significantly improves performance
        over checking clause satisfaction every time is_satisfied() is called.

        Args:
            variable: The variable that was flipped or assigned
            old_value: The old value of the variable
            new_value: The new value of the variable
        """
        positive_literal = Literal(variable, True)
        negative_literal = Literal(variable, False)

        affected_clauses = self.CNF.variables[variable]

        for clause in affected_clauses:
            # If it used to satisfy clause, remove literal from set of literals that was satisfying clause
            if old_value == 1:
                self.satisfied_literals[clause].discard(positive_literal)
            elif old_value == 0:
                self.satisfied_literals[clause].discard(negative_literal)

            # If it now satisfies the clause, add to set of literals that satisfy the clause
            if new_value == 1 and positive_literal in clause.literals:
                self.satisfied_literals[clause].add(positive_literal)
            elif new_value == 0 and negative_literal in clause.literals:
                self.satisfied_literals[clause].add(negative_literal)

            if self.satisfied_literals[clause]:
                self.unsatisfied_clauses.discard(clause)
            else:
                self.unsatisfied_clauses.add(clause)

    def is_satisfied(self) -> bool:
        """
        Check if the model satisfies the CNF formula.
        
        Returns:
            True if all clauses are satisfied, False otherwise
        """
        return not self.unsatisfied_clauses

    def get_make_and_break(self, var: Variable) -> Tuple[int, int]:
        """
        Calculate the make and break values if var is flipped.
        (make) minus (break) is the change in number of satisfied clauses,
        where positive means more satisfied
        
        Args:
            var: The variable to consider flipping
            
        Returns:
            make_count: number of unsatisfied clauses that would become satisfied
            break_count: number of satisfied clauses that would become unsatisfied
        """

        # TODO: implement get_make_and_break

        return 0, 0

    def get_unsatisfied_clauses(self) -> List[Clause]:
        """
        Output:
            list: A list of unsatisfied clauses in the model.
        """
        return list(self.unsatisfied_clauses)

    def check_sat_clauses(self) -> int:
        """
        Check the number of satisfied clauses for verification purposes.
        
        This method is used by staff to verify the backend is running correctly.
        
        Returns:
            Number of satisfied clauses
        """
        num_sat_clauses = 0
        for clause in self.CNF.clauses:
            for literal in clause.literals:
                variable = literal.variable
                if (self.assignment[variable] == 1 and literal.is_positive) or \
                   (self.assignment[variable] == 0 and not literal.is_positive):
                    num_sat_clauses += 1
                    break

        return num_sat_clauses
            


    def __str__(self) -> str:
        return str(self.assignment)


if __name__ == "__main__":
    # Example usage
    cnf = CNF()
    cnf.add_clause(
        Clause([Literal(Variable("A"), True), Literal(Variable("B"), True)]))
    cnf.add_clause(
        Clause([Literal(Variable("A"), False), Literal(Variable("C"), True)]))
    cnf.add_clause(
        Clause([Literal(Variable("B"), False), Literal(Variable("C"), False)]))

    print(cnf)

    my_model = Model(cnf)
    print("Current Assignments", my_model)
    print("Is satisfied?", my_model.is_satisfied())
    print("Num satisfied", my_model.check_sat_clauses())
    print("Unsatisfied clauses:", my_model.get_unsatisfied_clauses())

    my_model.assign(Variable("B"), False)
    print("Current Assignments", my_model)
    print("Is satisfied?", my_model.is_satisfied())
    print("Num satisfied", my_model.check_sat_clauses())
    print("Unsatisfied clauses:", my_model.get_unsatisfied_clauses())

    my_model.assign(Variable("C"), True)
    my_model.assign(Variable("A"), True)
    print("Current Assignments", my_model)
    print("Is satisfied?", my_model.is_satisfied())
    print("Num satisfied", my_model.check_sat_clauses())
    print("Unsatisfied clauses:", my_model.get_unsatisfied_clauses())