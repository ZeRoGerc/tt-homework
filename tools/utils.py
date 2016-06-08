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


def __subst__(exp: Expression, var_name: str, sub: Expression, free_vars: set, allowed: bool):
    """
    Replace all free entries of given variable in exp with sub.
    Throws VariableNotFreeException if variable is not free for substitution.

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


def substitution(exp: Expression, var_name: str, sub: Expression, ) -> Expression:
    """
    Replace all free entries of given variable in exp with sub.
    Throws VariableNotFreeException if variable is not free for substitution.

    :param exp: expression to replace variable in
    :param var_name: given variable
    :param sub: expression to substitute in place of all free entries of given variable
    :return: substituted expression
    """
    free_vars = get_free_vars(sub)
    return __subst__(exp, var_name, sub, free_vars, True)


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

    test_if_exception_raised_sub(parser_.parse("x x a \\a.a x c"),
                                 "x", parser_.parse("a b"))

    test_equality_of_sub(parser_.parse("a b c x (\\x.x)"),
                         "x", parser_.parse("\\x.x"),
                         parser_.parse("a b c (\\x.x) (\\x.x)"))

if __name__ == "__main__":
    test()
