from tools.terrors import InconsistentSystemError
from tools.tstructure import *


class Equation:
    def __init__(self, left: TType, right: TType):
        self.left = left
        self.right = right

    def __str__(self):
        return str(self.left) + "=" + str(self.right)

    def __hash__(self):
        return hash(self.left) ^ hash(self.right) ^ hash(self.__dict__)

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)


def __get_vars__(exp: TType) -> set:
    """
    Get all str(variables) of given expression.

    :param exp: given expression
    :return: set of variables
    """
    if isinstance(exp, TVar):
        return {exp.name}
    elif isinstance(exp, TImpl):
        return __get_vars__(exp.left).union(__get_vars__(exp.right))
    else:
        raise Exception("get_vars exception: No such type {0}".format(exp))


def __subst__(exp: TType, x: TVar, sub: TType) -> TType:
    """
    Substitute given variable in given expression on given substitution.

    :param exp: given expression
    :param var: given variable
    :param sub: given substitution
    :return: substituted expression
    """
    if isinstance(exp, TVar):
        if exp == x:
            return sub
        else:
            return exp
    elif isinstance(exp, TImpl):
        return TImpl(__subst__(exp.left, x, sub), __subst__(exp.right, x, sub))


def __apply_first__(equations: list) -> (bool, list):
    """
    Apply first type of transformation to the set of equations.
    First type is T=x -> x=T

    :param equations: given list
    :return: tuple(True if at least one transformation applied, transformed set of equations)
    """
    applied = False

    for i in range(len(equations)):
        if not isinstance(equations[i].left, TVar) and isinstance(equations[i].right, TVar):
            applied = True
            equations[i] = Equation(equations[i].right, equations[i].left)

    return applied, equations


def __apply_second__(equations: list) -> (bool, list):
    """
    Apply second type of transformation to the set of equations.
    Second type is T=T -> del

    :param equations: given list
    :return: tuple(True if at least one transformation applied, transformed set of equations)
    """

    result = []
    for equation in equations:
        if isinstance(equation.left, TVar) and equation.left.name in __get_vars__(equation.right):
            raise InconsistentSystemError("equation of type x=T and x in T")

        if equation.left != equation.right:
            result.append(equation)

    return len(result) != len(equations), result


def __apply_third__(equations: list) -> (bool, list):
    """
    Apply third type of transformation to the set of equations.
    Third type is A->B=C->D -> A=C, B=D

    :param equations: given list
    :return: tuple(True if at least one transformation applied, transformed set of equations)
    """
    result = []
    for equation in equations:
        if isinstance(equation.left, TImpl) and isinstance(equation.right, TImpl):
            result.append(Equation(equation.left.left, equation.right.left))
            result.append(Equation(equation.left.right, equation.right.right))
        else:
            result.append(equation)

    return len(result) != len(equations), result


def __apply_fourth__(equations: list) -> (bool, list):
    """
    Apply fourth type of transformation to the set of equations.
    Fourth type is x=T and S=R where (x in S or x in R)

    :param equations: given list
    :return: tuple(True if at least one transformation applied, transformed set of equations)
    """
    applied = False
    for i in range(len(equations)):
        vars = []
        for equation in equations:
            vars.append((__get_vars__(equation.left), __get_vars__(equation.right)))

        if isinstance(equations[i].left, TVar):
            x = equations[i].left
            for j in range(len(equations)):
                if i != j:
                    if (x.name in vars[j][0]) or (x.name in vars[j][1]):
                        applied = True
                        equations[j] = Equation(
                                __subst__(equations[j].left, x, equations[i].right),
                                __subst__(equations[j].right, x, equations[i].right)
                        )

    return applied, equations


def solve_set_of_equations(equations: list) -> list:
    temp_bool = True

    temp_eq = equations
    while temp_bool:
        temp_bool = False

        z, temp_eq = __apply_first__(temp_eq)
        temp_bool |= z

        z, temp_eq = __apply_second__(temp_eq)
        temp_bool |= z

        z, temp_eq = __apply_third__(temp_eq)
        temp_bool |= z

        z, temp_eq = __apply_fourth__(temp_eq)
        temp_bool |= z

    return temp_eq


def apply_system(exp: TType, equations: list) -> TType:
    """
    Apply given set of equations to given expression.
    This function assume that all equations is in the form x=T

    :param exp: given expression
    :param equations: given set of equation
    :return: resulting type
    """
    for equation in equations:
        if isinstance(equation.left, TVar):
            exp = __subst__(exp, equation.left, equation.right)

    return exp


def test():
    def test_equations(equations: list, result: list):
        print("Testing set of equations \n  {0} \nResult must be: \n  {1}".format(
                [str(i) for i in equations],
                [str(i) for i in result]))
        temp = solve_set_of_equations(equations)
        print("Result is:\n  {0}".format(
                [str(i) for i in temp]))
        assert temp == result
        print("Passed\n")

    def I(t1: TType, t2: TType) -> TImpl:
        return TImpl(t1, t2)

    t0 = TVar("t0")
    t1 = TVar("t1")
    t2 = TVar("t2")
    t3 = TVar("t3")
    t4 = TVar("t4")
    t5 = TVar("t5")
    t6 = TVar("t6")

    e0 = TVar("e0")
    e1 = TVar("e1")
    e2 = TVar("e2")
    e3 = TVar("e3")
    e4 = TVar("e4")
    e5 = TVar("e5")
    e6 = TVar("e6")

    eq1 = Equation(e4, I(I(t5, I(t6, t6)), e5))
    eq2 = Equation(t0, I(I(t2, I(t3, I(t4, e3))), e4))
    eq3 = Equation(e0, I(e2, e3))
    eq4 = Equation(e1, I(t4, e2))
    eq5 = Equation(t2, I(t3, e1))
    eq6 = Equation(t1, I(t3, e0))

    set1 = [eq1, eq2, eq3, eq4, eq5, eq6]
    print(str(apply_system(I(t0, I(t1, e5)), solve_set_of_equations(set1))))

    # TODO parser and tests


if __name__ == "__main__":
    test()
