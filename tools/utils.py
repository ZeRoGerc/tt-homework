from tools.tparsing import *
from tools.types import *


def get_free_vars(exp: Expression) -> set:
    """
    Method for getting set of free variables from Expression

    :param exp: expression for retrieving free variables
    :return: set of free variables
    """
    if isinstance(exp, Var):
        return {exp.name}
    elif isinstance(exp, Abstraction):
        answer = get_free_vars(exp.expression)
        if (exp.variable.name in answer):
            answer.remove(exp.variable.name)
        return answer
    elif isinstance(exp, Applique):
        left = get_free_vars(exp.left)
        right = get_free_vars(exp.right)
        return left.union(right)
    else:
        raise Exception("Unknown type of" + str(exp))


def __subst__(exp: Expression, var_name: str, sub: Expression, free_vars: set, allowed: bool):
    """
    Replace all free entries of given variable in exp with sub.
    Throws VariableNotFreeException if sub is not free for substitution.

    :param exp: expression to replace variable in
    :param var_name: given variable
    :param sub: expression to substitute in place of all free entries of given variable
    :param free_vars: set of all free variables os sub
    :param allowed: true is substitution allowed
    :return:
    """
    if isinstance(exp, Var):
        if exp.name == var_name:
            if allowed:
                return sub
            else:
                raise VariableIsNotFreeError(var_name + " not free")
        else:
            return exp
    elif isinstance(exp, Abstraction):
        if (exp.variable.name == var_name):
            return exp
        else:
            if exp.variable.name in free_vars:
                allowed_ = False
            else:
                allowed_ = allowed

            return Abstraction(exp.variable, __subst__(exp.expression, var_name, sub, free_vars, allowed_))
    elif isinstance(exp, Applique):
        return Applique(
                __subst__(exp.left, var_name, sub, free_vars, allowed),
                __subst__(exp.right, var_name, sub, free_vars, allowed)
        )
    else:
        raise Exception("Unknown type of" + str(exp))


def substitution(exp: Expression, var_name: str, sub: Expression) -> Expression:
    """
    Replace all free entries of given variable in exp with sub.
    Throws VariableNotFreeException if sub is not free for substitution.

    :param exp: expression to replace variable in
    :param var_name: given variable
    :param sub: expression to substitute in place of all free entries of given variable
    :return: substituted expression
    """
    free_vars = get_free_vars(sub)
    return __subst__(exp, var_name, sub, free_vars, True)


def __reduction__(exp: Expression) -> (bool, Expression):
    """
    Apply beta reduction in normalized order(left-most) once to given expression

    :param exp: given Expression
    :return: tuple(True is reduction occurred,  resulting expression)
    """
    if isinstance(exp, Var):
        return False, exp
    elif isinstance(exp, Abstraction):
        result = __reduction__(exp.expression)
        return result[0], Abstraction(exp.variable, result[1])
    elif isinstance(exp, Applique):
        left = __reduction__(exp.left)
        if left[0]:
            return True, Applique(left[1], exp.right)

        right = __reduction__(exp.right)
        if right[0]:
            return True, Applique(exp.left, right[1])

        cur = exp.left
        if isinstance(cur, Abstraction):
            try:
                result = substitution(cur.expression, cur.variable.name, exp.right)
                return True, result
            except VariableIsNotFreeError:
                return False, exp
        else:
            return False, exp


def reduction(exp: Expression) -> Expression:
    """
    Produce normalized form of given expression.
    If given expression doesn't have normalized form behavior is unspecified.

    :param exp: given Expression
    :return: normalized form of given expression
    """
    expression = rename_all_abstractions(exp)
    temp = __reduction__(expression)
    while temp[0]:
        temp = __reduction__(temp[1])

    return rename_all_abstractions(temp[1])


def __rename__(exp: Expression, last_var: int = 0) -> (int, Expression):
    """
    Rename all variables in given Expression, so that all Abstractions have different variables.

    :param exp: given expression
    :param last_var: last used variable
    :return: renamed expression
    """

    if isinstance(exp, Var):
        return last_var, exp
    elif isinstance(exp, Abstraction):
        new_var = Var(str(last_var + 1))
        result = __rename__(
                substitution(exp.expression, exp.variable.name, new_var),
                last_var + 1
        )

        return result[0], Abstraction(new_var, result[1])
    elif isinstance(exp, Applique):
        left = __rename__(exp.left, last_var)
        right = __rename__(exp.right, left[0])

        return right[0], Applique(left[1], right[1])


# noinspection PyTypeChecker
def __grammar_rename__(exp: Expression) -> Expression:
    """
    Rename variables in given expression so that they satisfy grammar

    :param exp: given expression
    :param var: last used variable
    :param renamed: renamed variables
    :return: renamed expression
    """
    if isinstance(exp, Var):
        if exp.name[0].isdigit():
            return Var("t" + exp.name)
        else:
            return exp
    elif isinstance(exp, Abstraction):
        return Abstraction(__grammar_rename__(exp.variable), __grammar_rename__(exp.expression))
    elif isinstance(exp, Applique):
        return Applique(__grammar_rename__(exp.left), __grammar_rename__(exp.right))


def rename_all_abstractions(exp: Expression) -> Expression:
    """
    Rename all variables in given Expression, so that all Abstractions have different variables.
    Renamed variables get such names: t1, t2, t3 ...

    :param exp: given expression
    :return: renamed expression
    """
    return __grammar_rename__(__rename__(exp)[1])


def test_free_vars():
    parser_ = BaseParser()

    def test_equality_of_free_vars(exp: Expression, result: set):
        print("Testing expression {0}: result must be '{1}'".format(exp, result))
        assert get_free_vars(exp) == result
        print("Passed\n")

    print("!!!Testing free variables...\n")

    test_equality_of_free_vars(parser_.parse("x \\x.x"), {"x"})
    test_equality_of_free_vars(parser_.parse("\\a.\\b.a"), set())
    test_equality_of_free_vars(parser_.parse("x \\a.\\b.x y z"), {"x", "y", "z"})
    test_equality_of_free_vars(parser_.parse("a b \\a.\\b.x a z"), {"a", "b", "x", "z"})


def test_sub():
    parser_ = BaseParser()

    def test_equality_of_sub(exp: Expression, var_name: str, sub: Expression, result: Expression):
        print("Testing substitution of variable '{0}' to '{1}' in expression '{2}': result must be '{3}'".format(
                var_name, sub, exp, result
        ))
        assert substitution(exp, var_name, sub) == result
        print("Passed\n")

    def test_if_exception_raised_sub(exp: Expression, var_name: str, sub: Expression):
        print(
                "Testing substitution of variable '{0}' to '{1}' in expression '{2}': Variable is not free expecting".format(
                        var_name, sub, exp
                ))
        try:
            substitution(exp, var_name, sub)
            assert False
        except VariableIsNotFreeError:
            print("Passed\n")

    print("!!!Testing substitution...\n")

    test_equality_of_sub(parser_.parse("x \\x.x"),
                         "x", parser_.parse("a b"),
                         parser_.parse("a b \\x.x"))

    test_equality_of_sub(parser_.parse("x x a \\x.a b c"),
                         "x", parser_.parse("a b"),
                         parser_.parse("(a b) (a b) a\\x.a b c"))

    test_if_exception_raised_sub(parser_.parse("x x a \\a.a x c"),
                                 "x", parser_.parse("a b"))

    test_equality_of_sub(parser_.parse("a b c x (\\x.x)"),
                         "x", parser_.parse("\\x.x"),
                         parser_.parse("a b c (\\x.x) (\\x.x)"))


def test_renaming():
    parser_ = BaseParser()

    def test_renaming(exp: Expression, result: Expression):
        print("Test renaming of '{0}': result must be '{1}'".format(exp, result))
        temp = rename_all_abstractions(exp)
        print("Result is '{0}'".format(temp))
        assert temp == result
        print("Passed")

    print("!!!Testing renaming...\n")

    test_renaming(
            parser_.parse("\\x.\\x.\\x.x"),
            Abstraction(
                    Var("t1"),
                    Abstraction(
                            Var("t2"),
                            Abstraction(Var("t3"), Var("t3"))
                    )
            ))

    test_renaming(
            parser_.parse("\\x.\\x.\\x.x a"),
            Abstraction(
                    Var("t1"),
                    Abstraction(
                            Var("t2"),
                            Abstraction(
                                    Var("t3"),
                                    Applique(
                                            Var("t3"),
                                            Var("a")
                                    )
                            )
                    ))
    )

    test_renaming(
            parser_.parse("(\\x.x) x a"),
            Applique(
                    Applique(
                            Abstraction(
                                    Var("t1"),
                                    Var("t1")
                            ),
                            Var("x")
                    ),
                    Var("a")
            )
    )


def alpha_eq(exp1: Expression, exp2: Expression) -> bool:
    """
    Test if two expression is alpha equivalent

    :param exp1: first expression
    :param exp2: second expression
    :return: True is equal False other wise
    """
    first = rename_all_abstractions(exp1)
    second = rename_all_abstractions(exp2)
    return first == second


def test_reduction():
    parser_ = BaseParser()

    def test_reduction(exp: Expression, result: Expression):
        print("Test reduction of '{0}': normalized form must be '{1}'".format(exp, result))
        temp = reduction(exp)
        print("Result is '{0}'".format(temp))
        assert alpha_eq(temp, result)
        print("Passed\n")

    print("!!!Testing reduction...\n")

    test_reduction(
            parser_.parse("(\\x.x) a"),
            parser_.parse("a")
    )

    test_reduction(
            parser_.parse("(\\x.x x x) (a b)"),
            parser_.parse("(a b) (a b) (a b)")
    )

    print("!!!Testing minus...\n")

    test_reduction(
            parser_.parse(type_minus + " {0} {1}".format(numbers[0], numbers[0])),
            parser_.parse(numbers[0])
    )

    test_reduction(
            parser_.parse(type_minus + " {0} {1}".format(numbers[2], numbers[1])),
            parser_.parse(numbers[1])
    )

    test_reduction(
            parser_.parse(type_minus + " {0} {1}".format(numbers[20], numbers[10])),
            parser_.parse(numbers[10])
    )

    print("!!!Testing power...\n")

    test_reduction(
            parser_.parse(type_pow + " {0} {1}".format(numbers[10], numbers[0])),
            parser_.parse(numbers[1])
    )

    test_reduction(
            parser_.parse(type_pow + " {0} {1}".format(numbers[0], numbers[20])),
            parser_.parse(numbers[0])
    )

    test_reduction(
            parser_.parse(type_pow + " {0} {1}".format(numbers[10], numbers[1])),
            parser_.parse(numbers[10])
    )

    test_reduction(
            parser_.parse(type_pow + " {0} {1}".format(numbers[3], numbers[3])),
            parser_.parse(numbers[27])
    )

    print("!!!Testing power2...\n")

    test_reduction(
            parser_.parse(type_pow2 + " {0} {1}".format(numbers[3], numbers[3])),
            parser_.parse(numbers[27])
    )


def test():
    test_free_vars()
    test_sub()
    test_renaming()
    test_reduction()


if __name__ == "__main__":
    test()
