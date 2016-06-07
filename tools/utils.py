from tools.tparsing import *


def get_free_vars(exp: Expression) -> set:
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


def test():
    def test_equality(exp: Expression, result: set):
        print("Testing expression {0}: result must be {1}".format(exp, result))
        assert get_free_vars(exp) == result
        print("Passed\n")

    print("!!!Testing free variables...\n")
    parser_ = BaseParser()

    test_equality(parser_.parse("x \\x.x"), {"x"})
    test_equality(parser_.parse("\\a.\\b.a"), set())
    test_equality(parser_.parse("x \\a.\\b.x y z"), {"x", "y", "z"})
    test_equality(parser_.parse("a b \\a.\\b.x a z"), {"a", "b", "x", "z"})


if __name__ == "__main__":
    test()
