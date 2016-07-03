from tools.tstructure import *
from tools.utils import rename_all_abstractions
from tools.equations import subst, solve_set_of_equations, Equation
import time

def __remove_quantifiers__(exp: TType) -> (TType, list):
    """
    Produce expression without quantifiers from given expression
    :param exp: given expression
    :return: tuple(expression without quantifiers, list of connected variables)
    """
    if isinstance(exp, TUni):
        result = __remove_quantifiers__(exp.expression)
        result[1].append(exp.var)
        return result[0], result[1]
    else:
        return exp, []


def copy(gamma: dict) -> dict:
    result = {}
    for key in gamma:
        result[key] = gamma[key]
    return result

def __get_free_vars__(t: TType, connected_vars: set) -> set:
    """
    Produce set of all free variables of given type.
    :param t: given type
    :param connected_vars: already connected variables
    :return: set of connected variables
    """
    if isinstance(t, TVar):
        if t.name in connected_vars:
            return set()
        else:
            return {t.name}
    elif isinstance(t, TImpl):
        s1 = __get_free_vars__(t.left, connected_vars)
        s2 = __get_free_vars__(t.right, connected_vars)
        return s1.union(s2)
    elif isinstance(t, TUni):
        connected_vars.add(t.var.name)
        return __get_free_vars__(t.expression, connected_vars)


def get_free_vars(t: TType) -> set:
    """
    Produce set of all free variables of given type.
    :param t: given type
    :return: set of connected variables
    """
    return __get_free_vars__(t, set())


class WAlgorithm:
    def __init__(self):
        self.last_number = 0
        self.defined_variables = {}
        self.inst = []

    def get_new_type(self) -> TVar:
        """
        Produce new type as a variable that do not satisfy grammar.
        :return: new type
        """
        self.last_number += 1
        return TVar("type" + str(self.last_number))

    @staticmethod
    def __context_substitution__(s1: dict, s2: dict) -> dict:
        """
        Produce applying of s1 to gamma
        :param s1: context
        :param gamma: context
        :return: applying of two contexts
        """
        new_context = copy(s2)
        for var in new_context.keys():
            for sub in s1.keys():
                assert isinstance(sub, TVar)
                new_context[var] = subst(new_context[var], sub, s1[sub])
        return new_context

    @staticmethod
    def __merge_substitutions__(s1: dict, s2: dict) -> dict:
        """
        Merge two contexts (subst and merge)
        """
        new_context = WAlgorithm.__context_substitution__(s1, s2)
        for var in s1.keys():
            assert isinstance(var, TVar)
            new_context[var] = s1[var]

        return new_context

    @staticmethod
    def __apply_substitution(s1: dict, t: TType):
        """
        Apply substitution to the given type
        :param s1: substitution (context)
        :param t: given tyoe
        :return: substituted type
        """
        for var in s1:
            assert isinstance(var, TVar)
            t = subst(t, var, s1[var])
        return t

    @staticmethod
    def locking(s1: dict, t: TType) -> TType:
        """
        Produce @a1.@a2.@a3...t where ai in free(t) and not in free(s1)
        :param s1: context
        :param t: given type
        :return: locked type
        """
        context_free_vars = set()
        for exp in s1.values():
            context_free_vars.union(get_free_vars(exp))

        exp_free_vars = get_free_vars(t)
        need_connect = exp_free_vars - context_free_vars

        result = t
        for var in need_connect:
            result = TUni(TVar(var), result)
        return result

    def __infer_type__(self, gamma: dict, exp: Expression) -> (dict, TType):
        """
        Infer the type of given expression in given context.
        So that Subst(gamma)|- exp : type
        :param gamma: given context
        :param exp: given expression
        :return: tuple(substitution, inferred type)
        """
        if isinstance(exp, Var):
            if TVar(exp.name) in gamma:
                cur_type, vars = __remove_quantifiers__(gamma[TVar(exp.name)])
                for variable in vars:
                    cur_type = subst(cur_type, variable, self.get_new_type())
                if len(vars) > 0:
                    self.inst.append(Equation(TVar(exp.name), cur_type))
                return {}, cur_type

            new_type = self.get_new_type()
            self.defined_variables[TVar(exp.name)] = new_type
            return {}, new_type

        elif isinstance(exp, Applique):
            s1, t1 = self.__infer_type__(gamma, exp.left)
            new_gamma = WAlgorithm.__merge_substitutions__(s1, copy(gamma))
            s2, t2 = self.__infer_type__(new_gamma, exp.right)

            t3 = WAlgorithm.__apply_substitution(s2, t1)
            betta = self.get_new_type()
            v = solve_set_of_equations([Equation(t3, TImpl(t2, betta)), ])
            sub_v = {}
            for equation in v:
                assert isinstance(equation.left, TVar)
                sub_v[TVar(equation.left.name)] = equation.right

            s = WAlgorithm.__merge_substitutions__(
                sub_v,
                WAlgorithm.__merge_substitutions__(s1, s2)
            )
            return s, WAlgorithm.__apply_substitution(s, betta)

        elif isinstance(exp, Abstraction):
            new_gamma = copy(gamma)
            if TVar(exp.variable.name) in new_gamma:
                del new_gamma[TVar(exp.variable.name)]
            betta = self.get_new_type()
            self.defined_variables[TVar(exp.variable.name)] = betta

            new_gamma[TVar(exp.variable.name)] = betta
            s1, t1 = self.__infer_type__(new_gamma, exp.expression)
            return s1, TImpl(WAlgorithm.__apply_substitution(s1, betta), t1)

        else:
            assert isinstance(exp, Let)
            new_gamma = copy(gamma)
            s1, t1 = self.__infer_type__(new_gamma, exp.subst)

            x_type = WAlgorithm.locking(WAlgorithm.__merge_substitutions__(s1, new_gamma), t1)

            if TVar(exp.variable.name) in new_gamma:
                del new_gamma[TVar(exp.variable.name)]

            new_gamma = WAlgorithm.__merge_substitutions__(s1, new_gamma)
            new_gamma[TVar(exp.variable.name)] = x_type

            s2, t2 = self.__infer_type__(new_gamma, exp.expression)

            s = WAlgorithm.__merge_substitutions__(s2, s1)
            # s[TVar(exp.variable.name)] = x_type
            return s, t2

    def infer_type(self, exp: Expression) -> (dict, TType):
        """
        Exp must be with renamed abstractions
        Infer the type of given expression in given context.
        So that Subst(gamma)|- exp : type
        :param exp: given expression
        :return: tuple(substitution, inferred type)
        """
        self.last_number = 0
        self.defined_variables = {}
        self.inst = []
        context, result = self.__infer_type__({}, exp)
        for sub in self.defined_variables.keys():
            context[sub] = self.defined_variables[sub]

        # for beauty in output
        eq = []
        eq_temp = []
        for key in context.keys():
            if not isinstance(context[key], TUni):
                eq.append(Equation(key, context[key]))
            else:
                eq_temp.append(Equation(key, context[key]))

        eq_solve = solve_set_of_equations(eq)
        context = {}
        for equation in eq_solve:
            context[equation.left] = equation.right
        for equation in eq_temp:
            context[equation.left] = equation.right

        return context, result


def run_test(exp: Expression):
    infer = WAlgorithm()
    exp = rename_all_abstractions(exp)
    print("Testing expression: {0}".format(exp))
    time.sleep(0.1)

    context, result = infer.infer_type(exp)
    print("context:")
    for key in context.keys():
        print("{0} : {1}".format(key, context[key]))
    time.sleep(0.1)

    print("result: {0}".format(result))
    time.sleep(0.1)

    print("Passed\n")
    time.sleep(0.1)

    time.sleep(0.5)


def test():
    x = Var("x")
    y = Var("y")
    z = Var("z")

    constant = Abstraction(x, y)
    id = Abstraction(x, x)
    fst = Abstraction(x, Abstraction(y, x))

    # run_test(x)
    #
    # run_test(constant)
    # run_test(id)
    # run_test(Applique(Var("x"), Var("y")))
    # run_test(Applique(id, z))
    #
    # fst = Abstraction(x, Abstraction(y, x))
    # run_test(fst)
    #
    # run_test(Applique(fst, x))
    # run_test(Applique(fst, y))
    # run_test(Applique(Applique(fst, x), y))


    pre_good_test = Let(
        Var("id"),
        Abstraction(Var("x"), Var("x")),
        Applique(Var("id"), Var("y"))
    )
    run_test(pre_good_test)


    good_test = Let(
        Var("id"),
        id,
        Let(
            Var("fst"),
            fst,
            Applique (
                Applique(
                    Var("fst"),
                    Applique(Var("id"), Var("x"))
                ),
                Applique(Var("id"), Var("y"))
            )
        )
    )
    run_test(good_test)


if __name__ == "__main__":
    test()