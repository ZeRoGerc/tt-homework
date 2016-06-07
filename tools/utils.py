from tools.tparsing import *


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


def substitution(exp: Expression, var_name: str, sub: Expression) -> Expression:
    """
    Replace all free entries of given variable in exp with sub

    :param exp: expression to replace variable in
    :param var_name: given variable
    :param sub: expression to substitute in place of all free entries of given variable
    :return: substituted expression
    """
    if isinstance(exp, Var):
        if exp.name == var_name:
            return sub
        else:
            return exp
    elif isinstance(exp, Abstraction):
        if (exp.variable.name == var_name):
            return exp
        else:
            return Abstraction(exp.variable, substitution(exp.expression, var_name, sub))
    elif isinstance(exp, Applique):
        return Applique(
                substitution(exp.left, var_name, sub),
                substitution(exp.right, var_name, sub)
        )
    else:
        raise Exception("Unknown type of" + str(exp))


def test():
    def test_equality_of_free_vars(exp: Expression, result: set):
        print("Testing expression {0}: result must be '{1}'".format(exp, result))
        assert get_free_vars(exp) == result
        print("Passed\n")

    def test_equality_of_sub(exp: Expression, var_name: str, sub: Expression, result: Expression):
        print("Testing substitution of variable '{0}' to '{1}' in expression '{2}': result must be '{3}'".format(
                var_name, sub, exp, result
        ))
        assert substitution(exp, var_name, sub) == result
        print("Passed\n")

    print("!!!Testing free variables...\n")
    parser_ = BaseParser()

    test_equality_of_free_vars(parser_.parse("x \\x.x"), {"x"})
    test_equality_of_free_vars(parser_.parse("\\a.\\b.a"), set())
    test_equality_of_free_vars(parser_.parse("x \\a.\\b.x y z"), {"x", "y", "z"})
    test_equality_of_free_vars(parser_.parse("a b \\a.\\b.x a z"), {"a", "b", "x", "z"})

    print("!!!Testing substitution...\n")

    test_equality_of_sub(parser_.parse("x \\x.x"),
                         "x", parser_.parse("a b"),
                         parser_.parse("a b \\x.x"))

    test_equality_of_sub(parser_.parse("x x a \\x.a b c"),
                         "x", parser_.parse("a b"),
                         parser_.parse("(a b) (a b) a\\x.a b c"))

if __name__ == "__main__":
    test()
