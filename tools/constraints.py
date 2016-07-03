from tools.tstructure import *
from tools.equations import *
import time


class ConstraintResolver:

    def __init__(self):
        self.last_number = 0
        self.variable_map = {}

    def generate_constraint(self, exp: Expression, t: TType) -> Constraint:
        """
        Generate constraint to the given expression with the given type
        """
        if isinstance(exp, Var):
            return CRelationL(TVar(exp.name), t)

        elif isinstance(exp, Abstraction):
            a1 = self.get_new_type()
            a2 = self.get_new_type()
            left_def = CDef(TVar(exp.variable.name), TSigma([], None, a1), self.generate_constraint(exp.expression, a2))
            right = CRelationEq(TImpl(a1, a2), t)
            return CExistence(a1, CExistence(a2, CAnd(left_def, right)))

        elif isinstance(exp, Applique):
            a = self.get_new_type()
            left = self.generate_constraint(exp.left, TImpl(a, t))
            right = self.generate_constraint(exp.right, a)
            return CExistence(a, CAnd(left, right))

        elif isinstance(exp, Let):
            a = self.get_new_type()
            x = TVar(exp.variable.name)
            sigma = TSigma([a, ], self.generate_constraint(exp.subst, a), a)
            right_and = CAnd(
                CRelationL(x, a),
                self.generate_constraint(exp.expression, t)
            )
            return CDef(x, sigma, right_and)
        else:
            assert False

    def get_new_type(self) -> TVar:
        """
        Produce new type as a variable that do not satisfy grammar.
        :return: new type
        """
        self.last_number += 1
        return TVar("t" + str(self.last_number))

    def __remember_types__(self, const: Constraint):
        """
        Find (x < t) and remember them in self.variable_map
        :param const: constraint
        """
        if isinstance(const, CRelationL) and isinstance(const.left, TVar):
            self.variable_map[const.left] = const.right
        elif isinstance(const, CAnd):
            self.__remember_types__(const.left)
            self.__remember_types__(const.right)
        elif isinstance(const, CExistence):
            self.__remember_types__(const.constraint)
        elif isinstance(const, CDef):
            self.__remember_types__(const.constraint)

    def __rename_answer__(self, t : TType):
        if isinstance(t, TVar):
            if t in self.variable_map:
                return self.variable_map[t]
            else:
                return t
        elif isinstance(t, TImpl):
            return TImpl(
                self.__rename_answer__(t.left),
                self.__rename_answer__(t.right)
            )
        elif isinstance(t, TUni):
            return TUni(
                t.var,
                self.__rename_answer__(t.expression)
            )
        else:
            assert False

    @staticmethod
    def __generalization__(t: TType, defined: list, phi: dict) -> TType:
        """
        Generate CSigma with variables that in phi but not in defined
        """
        # TODO: test this
        vars = set(defined)
        result = []
        for var in phi.keys():
            if isinstance(phi, Var) and (var not in vars):
                result += var

        return TSigma(list(vars), None, t)

    def __substitution__(self, x: TVar, subst: TType, c: Constraint) -> Constraint:
        """
        Substitute all occurrences of x in c by subst
        """
        if isinstance(c, CRelationL):
            if c.left == x:
                return CRelationL(subst, c.right)
            else:
                return c
        elif isinstance(c, CRelationEq):
            return c
        elif isinstance(c, CAnd):
            left = self.__substitution__(x, subst, c.left)
            right = self.__substitution__(x, subst, c.right)
            return CAnd(left, right)
        elif isinstance(c, CExistence):
            return CExistence(c.var, self.__substitution__(x, subst, c.constraint))
        elif isinstance(c, CDef):
            return CDef(c.var, c.sigma, self.__substitution__(x, subst, c.constraint))
        else:
            assert False

    def __inst__(self, c: TSigma) -> TType:
        """
        Instantiate CSigma (@a.exp -> exp[a := b] where b is a new type)
        """
        exp = c.type
        for var in c.vars:
            exp = subst(exp, var, self.get_new_type())

        return exp

    def __resolve__(self, const: Constraint, defined: list) -> dict:
        """

        :param const:
        :return:
        """
        if isinstance(const, CExistence):
            # Just skip existence quantifier
            return self.__resolve__(const.constraint, defined)

        elif isinstance(const, CRelationEq):
            # We latter will use it for unification
            return {const.right: const.left}

        elif isinstance(const, CRelationL):
            if isinstance(const.left, TSigma) and (const.left.constraint is None):
                return {const.right: self.__inst__(const.left)}
            elif isinstance(const.left, TVar):
                return {const.right: const.left}

        elif isinstance(const, CAnd):
            phi1 = self.__resolve__(const.left, defined)
            phi2 = self.__resolve__(const.right, defined)

            eq = []
            for key in phi1.keys():
                eq.append(Equation(key, phi1[key]))

            for key in phi2.keys():
                eq.append(Equation(key, phi2[key]))

            temp = solve_set_of_equations(eq)
            result = {}
            # all equation#left is different because system is right form
            for equation in temp:
                result[equation.left] = equation.right

            return result

        elif isinstance(const, CDef):
            # Only two variants: def - len(vars) = 0, let - len(vars) = 1
            assert (len(const.sigma.vars) <= 1)

            temp = const.sigma.type

            if len(const.sigma.vars) == 1:  # def x : @a[C].exp in [] (let)
                phi = self.__resolve__(const.sigma.constraint, defined)

                # phi[alpha]
                if const.sigma.vars[0] in phi:
                    temp = phi[const.sigma.vars[0]]
                else:
                    assert False

                temp = self.__generalization__(temp, defined, phi)

            new_def = defined
            new_def.append(temp)
            new_const = self.__substitution__(const.var, temp, const.constraint)
            return self.__resolve__(new_const, new_def)

        else:
            assert False

    def resolve(self, const: Constraint, exp_type : TType) -> TType:
        self.variable_map = {}
        self.__remember_types__(const)
        phi = self.__resolve__(const, [])
        return self.__rename_answer__(phi[exp_type])


def run_test(exp: Expression):
    infer = ConstraintResolver()
    print("Testing expression: {0}".format(exp))
    time.sleep(0.1)

    result_type = TVar("result")
    constraint = infer.generate_constraint(exp, result_type)
    print(constraint)
    time.sleep(0.1)

    print(infer.resolve(constraint, result_type))
    time.sleep(0.1)

    print("Passed\n")
    time.sleep(0.1)

    time.sleep(0.5)


def test():
    infer = ConstraintResolver()

    abs1 = Abstraction(
        Var("x"),
        Var("y")
    )

    exp = Applique(
        abs1,
        Var("x")
    )

    print(ConstraintResolver().generate_constraint(Var("x"), TVar("t1")))
    print(ConstraintResolver().generate_constraint(abs1, TVar("t2")))
    print(ConstraintResolver().generate_constraint(exp, TVar("t3")))
    print("Pretests passed\n")

    run_test(Var("x"))
    run_test(abs1)
    run_test(exp)
    run_test(Abstraction(Var("y"), exp))

    pre_good_test = Let(
        Var("id"),
        Abstraction(Var("x"), Var("x")),
        Applique(Var("id"), Var("y"))
    )
    run_test(pre_good_test)

    good_test = Let(
        Var("id"),
        Abstraction(Var("x"), Var("x")),
        Let(
            Var("fst"),
            Abstraction(Var("x"), Abstraction(Var("y"), Var("x"))),
            Applique(
                Applique(
                    Var("fst"),
                    Applique(Var("id"), Var("x")),
                ),
                Applique(Var("id"), Var("y"))
            )
        )
    )
    run_test(good_test)



if __name__ == "__main__":
    test()