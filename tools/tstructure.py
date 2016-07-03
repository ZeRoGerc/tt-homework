import re


class Expression:
    """
        Just for consistency. Use this class to ensure you get instance of either Var, Applique or Abstraction
    """

    variable_match = re.compile("[a-z][a-z\d']*")

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)


class Var(Expression):
    """
        This is variable of expression. It matches the regular expression stored in the field regexp
    """

    def __init__(self, name: str):
        self.name = name

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name


class Applique(Expression):
    """
        Expression of type XX
    """

    def __init__(self, left: Expression, right: Expression):
        self.left = left
        self.right = right

    def __hash__(self):
        return hash(self.left) ^ hash(self.right) 

    @staticmethod
    def __wrap__(exp: Expression):
        if isinstance(exp, Var) or isinstance(exp, Abstraction):
            return str(exp)
        else:
            return "(" + str(exp) + ")"

    def __str__(self):
        return "(" + " ".join((str(self.left), str(self.right))) + ")"


class Abstraction(Expression):
    """
        Expression of type x\.X
    """

    def __init__(self, variable: Var, expression: Expression):
        self.variable = variable
        self.expression = expression

    def __hash__(self):
        return hash(self.variable) ^ hash(self.expression) 

    def __str__(self):
        return "(\\" + str(self.variable) + "." + str(self.expression) + ")"


class Let(Expression):
    """
        let = expr in expr.
        For extended grammar
    """

    def __init__(self, variable: Var, subst: Expression, expression: Expression):
        self.variable = variable
        self.subst = subst
        self.expression = expression

    def __hash__(self):
        return hash(self.variable) ^ hash(self.subst) ^ hash(self.expression) 

    def __str__(self):
        return "(let " + str(self.variable) + "=" + str(self.subst) + " in " + str(self.expression) + ")"


class TType:
    """
        Base class for all types
    """

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


class TVar(TType):
    """
        Atomic unit of all TTypes
    """

    def __init__(self, name: str):
        self.name = name

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name


class TImpl(TType):
    """
        Implication for TType forming.
    """

    def __init__(self, left: TType, right: TType):
        self.left = left
        self.right = right

    def __hash__(self):
        return hash(self.left) ^ hash(self.right) 

    def __str__(self):
        return "(" + str(self.left) + "->" + str(self.right) + ")"


class TUni(TType):
    """
        Universal quantifier
    """

    def __init__(self, var: TVar, exp: TType):
        self.var = var
        self.expression = exp

    def __hash__(self):
        return hash(self.var) ^ hash(self.expression) 

    def __str__(self):
        return "(@" + str(self.var) + "." + str(self.expression) + ")"


class Constraint:
    """
        Base class for all constraints
    """

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


class CRelationL(Constraint):
    """
        Relation constraint (x < t)
    """

    def __init__(self, left: TType, right: TType):
        self.left = left
        self.right = right

    def __hash__(self):
        return hash(self.left) ^ hash(self.right) 

    def __str__(self):
        return "(" + str(self.left) + "<" + str(self.right) + ")"


class CRelationEq(Constraint):
    """
        Equality constraint (t = t)
    """

    def __init__(self, left: TType, right: TType):
        self.left = left
        self.right = right

    def __hash__(self):
        return hash(self.left) ^ hash(self.right) 

    def __str__(self):
        return "(" + str(self.left) + "=" + str(self.right) + ")"


class CAnd(Constraint):
    """
        And constraint
    """

    def __init__(self, left: Constraint, right: Constraint):
        self.left = left
        self.right = right

    def __hash__(self):
        return hash(self.left) ^ hash(self.right) 

    def __str__(self):
        return "(" + str(self.left) + "&" + str(self.right) + ")"


class CExistence(Constraint):
    """
        Existence constraint
    """

    def __init__(self, var: TVar, constraint: Constraint):
        self.var = var
        self.constraint = constraint

    def __hash__(self):
        return hash(self.var) ^ hash(self.constraint) 

    def __str__(self):
        return "(?" + str(self.var) + "." + str(self.constraint) + ")"


class TSigma(TType):
    """
    Sigma constraint @
    vars is the list of TVars
    vars can be empty, constraint can be None
    """

    def __init__(self, vars: list, constraint: Constraint, type: TType):
        self.vars = vars
        self.constraint = constraint
        self.type = type

    def __hash__(self):
        return hash(tuple(self.vars)) ^ hash(self.constraint) ^ hash(self.type)

    def __str__(self):
        constraints = ""
        if self.constraint is not None:
            constraints = str(self.constraint)
        vars = ""
        for var in self.vars:
            vars += str(var) + " "

        return "@" + vars + "[" + constraints + "]" + "." + str(self.type)


class CDef(Constraint):
    """
        Def constraint
    """

    def __init__(self, var: TVar, sigma: TSigma, constraint: Constraint):
        self.var = var
        self.sigma = sigma
        self.constraint = constraint

    def __hash__(self):
        return hash(self.var) ^ hash(self.sigma) ^ hash(self.constraint) 

    def __str__(self):
        return "(def " + str(self.var) + ":" + str(self.sigma) + " in " + str(self.constraint) + ")"
