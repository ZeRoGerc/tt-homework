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
        return hash(self.left) ^ hash(self.right) ^ hash((self.left, self.right))

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
        return hash(self.variable) ^ hash(self.expression) ^ hash((self.variable, self.expression))

    def __str__(self):
        return "(\\" + str(self.variable) + "." + str(self.expression) + ")"
