"""
    Parser that match grammar of first homework
"""
from tools.terrors import *
from tools.tstructure import *
from tools.types import *


class BaseParser:
    def __init__(self):
        self.raw_string = ""

    def __trim__(self, id: int) -> int:
        """
        Skip whitespaces in self.raw_string from given index.

        :param id: given index
        :return current id of non whitespace symbol or len(self.raw_string) if end of string reached
        """
        while id < len(self.raw_string) and self.raw_string[id] == ' ':
            id += 1

        return id

    def __find_next__(self, index: int, symbol: str) -> int:
        """
        Skip whitespaces and return position of symbol in self.raw_string

        :param index: id to stat search
        :param symbol: symbol to search
        :return: index of symbol
        """
        id = self.__trim__(index)
        if id >= len(self.raw_string) or self.raw_string[id] != symbol:
            raise self.__invalid_expression_error__(id)
        else:
            return id

    def __invalid_expression_error__(self, id: int) -> InvalidExpressionError:
        return InvalidExpressionError("Starting from index: {0}".format(id) +
                                      ", Chunk is: '" +
                                      self.raw_string[id: min(id + 5, len(self.raw_string))] +
                                      "'")

    def parse_variable(self, index: int) -> (int, Var):
        """
        Parse single variable starting from given index of self.raw_string

        :param index: index of self.raw_string to start parsing from
        :return: tuple(length of parsed symbols(including whitespaces), parsed variable)
        """
        id = self.__trim__(index)

        if id >= len(self.raw_string):
            raise self.__invalid_expression_error__(id)

        name = Expression.variable_match.match(self.raw_string, pos=id)
        if name is None:
            raise self.__invalid_expression_error__(id)
        else:
            id = name.end()
            variable = Var(name.group())
            return id - index, variable

    def parse_atom(self, index: int) -> (int, Expression):
        """
        Parse single atom from given position of self.raw_string
        Atom ::= (Expression) | Variable

        :param index: index of self.raw_string to start parsing from
        :return: tuple(length of parsed symbols(including whitespaces), parsed atom)
        """
        id = self.__trim__(index)

        if id >= len(self.raw_string):
            raise self.__invalid_expression_error__(id)

        if self.raw_string[id] == '(':
            id += 1
            answer = self.parse_expression(id)

            parsed_len = self.__find_next__(id + answer[0], ')') - index + 1
            return parsed_len, answer[1]
        else:
            return self.parse_variable(index)

    def parse_applique(self, index: int) -> (int, Expression):
        """
        Parse single application starting from given position of self.raw_string

        :param index: index of self.raw_string to start parsing from
        :return: tuple(length of parsed symbols(including whitespaces), parsed applique)
        """
        id = index
        answer = []
        while id < len(self.raw_string):
            try:
                temp = self.parse_atom(id)
                id += temp[0]
                answer.append(temp[1])
            except InvalidExpressionError:
                break

        def get_answer(end_index: int):
            if end_index == 0:
                return answer[0]
            else:
                return Applique(get_answer(end_index - 1), answer[end_index])

        return id - index, get_answer(len(answer) - 1)

    def parse_abstraction(self, index: int) -> (int, Abstraction):
        """
        Parse single application starting from given position of self.raw_string

        :param index: index of self.raw_string to start parsing from
        :return: tuple(length of parsed symbols(including whitespaces), parsed abstraction)
        """
        id = self.__trim__(index)

        if self.raw_string[id] != '\\':
            raise self.__invalid_expression_error__(id)
        else:
            id += 1  # Skip \
            variable_ = self.parse_variable(id)
            id = self.__find_next__(id + variable_[0], '.') + 1  # Also skip .
            exp = self.parse_expression(id)
            return id + exp[0] - index, Abstraction(variable_[1], exp[1])

    def parse_expression(self, index: int) -> (int, Expression):
        """
        Parse string stored in self.raw_string.

        :param index: index of self.raw_string to start parsing from
        :return: tuple(length of parsed symbols(including whitespaces), parsed expression)
        """
        id = self.__trim__(index)

        if id >= len(self.raw_string):
            raise self.__invalid_expression_error__(id)

        if self.raw_string[id] != '\\':
            #  When application must be first
            temp = self.parse_applique(id)
            id = self.__trim__(id + temp[0])

            # It can also be \a.exp
            if id >= len(self.raw_string) or self.raw_string[id] != '\\':
                return id - index, temp[1]  # Case when expression ::= application
            else:
                abstract = self.parse_abstraction(id)
                return id + abstract[0] - index, Applique(temp[1], abstract[1])
        else:
            return self.parse_abstraction(index)

    def parse(self, for_parse: str):
        self.raw_string = for_parse
        try:
            return self.parse_expression(0)[1]
        except InvalidExpressionError as err:
            print(err)


def test():
    parser_ = BaseParser()

    def test_stability(raw: str, additional=None):
        if additional is not None:
            print(additional)

        print("Ensuring parser will not crash on string '{0}'".format(raw))
        print("Result of work is: '{0}'".format(parser_.parse(raw)))
        print("Passed\n")

    def test_equality(raw: str, result: str, additional=None):
        if additional is not None:
            print(additional)

        print("Testing string '{0}' must be equal to {1}".format(raw, result))
        parsed_ = str(parser_.parse(raw))
        print("Result of work is: '{0}'".format(parsed_))
        assert (parsed_ == result)
        print("Passed\n")

    print("!!!Testing some random tests...\n")
    test_equality("x \\x.x", "(x (\\x.x))")
    test_equality("\\x.\\y.x", "(\\x.(\\y.x))")
    test_equality("x", "x")
    test_equality("\\a.\\b.a b c (\\d.e \\f.g) h", "(\\a.(\\b.((((a b) c) (\d.(e (\\f.g)))) h)))")
    test_stability("\\a.\\b.  a (  b)  c")
    test_stability("\\ a  . \\b  .   (a  b)  c     (  \\ d . e   \\ f .  g )   (((h)))")
    test_stability("\\ a  . \\b  .   ( (   ( a  ) )   ) (  b )  c     (  \\ d . e   \\ f .  g )   h")

    print("!!!Testing standard functions...\n")

    test_stability(type_true, "True")

    test_stability(type_false, "False")

    test_stability(type_not, "Not")

    test_stability(numbers[0], "Zero")

    test_stability(numbers[1], "One")

    test_stability(type_is_zero, "isZero")

    test_stability(type_is_even, "isEven")

    test_stability(type_add, "Add")

    test_stability(type_mul, "Mul")

    test_stability(type_pow, "Pow")

    test_stability(type_pow2, "Pow'")

    test_stability(type_minus, "Minus")


if __name__ == "__main__":
    test()
