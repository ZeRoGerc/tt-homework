class InvalidExpressionError(Exception):
    def __init__(self, message: str):
        Exception.__init__(self, "Invalid string passed as argument. Error occurred: {0}".format(message))
