class InvalidExpressionError(Exception):
    def __init__(self, message: str):
        Exception.__init__(self, "Invalid string passed as argument. Error occurred: {0}".format(message))


class VariableIsNotFreeError(Exception):
    def __init__(self, message: str):
        Exception.__init__(self, "Variable for substitution is not free. Error occured: {0}".format(message))
