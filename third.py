import getopt
import os
import sys

from tools.terrors import VariableIsNotFreeError
from tools.tparsing import BaseParser
from tools.tstructure import *
from tools.utils import substitution


def solve(input_file, output_file):
    parser_ = BaseParser()
    temp = input_file.readline()

    exp = parser_.parse(temp[:temp.find('[')])
    var_name = Expression.variable_match.match(temp, pos=temp.find('[') + 1)
    var_name = var_name.group()

    if var_name is None:
        print("Invalid variable")
        sys.exit(1)

    sub = parser_.parse(temp[temp.find(":=") + 2: temp.find("]")])

    try:
        result = substitution(exp, var_name, sub)
        output_file.write(str(result))
    except VariableIsNotFreeError:
        output_file.write("Нет свободы для подстановки для переменной {0}".format(var_name))


def main(argv):
    input_file = 'tes.in'
    output_file = 'tes.out'

    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["input_file=", "output_file="])
    except getopt.GetoptError:
        print("first.py -i <input_file> -o <output_file>")
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-h":
            print("third.py -i <input_file> -o <output_file>")
            sys.exit()
        elif opt in ("-i", "-input_file"):
            input_file = arg
        elif opt in ("-o", "-output_file"):
            output_file = arg

    script_path = os.path.dirname(__file__)
    input_ = open(os.path.join(script_path, input_file), "r")
    output_ = open(os.path.join(script_path, output_file), "w")

    solve(input_, output_)


if __name__ == "__main__":
    main(sys.argv[1:])
