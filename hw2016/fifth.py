import getopt
import os
import sys

from tools.tparsing import BaseParser
from tools.constraints import *
from tools.tstructure import TVar


def solve(input_file, output_file):
    infer = ConstraintResolver()
    parser_ = BaseParser()
    temp = input_file.readline()

    exp = parser_.parse(temp)
    result_type = TVar("result")
    constraint = infer.generate_constraint(exp, result_type)

    output_file.write(str(infer.resolve(constraint, result_type)) + "\n")

    for eq in set(infer.inst):
        if eq.left in infer.variable_map:
            del infer.variable_map[eq.left]
        output_file.write(str(eq.left) + " : " + str(eq.right) + "\n")

    for eq in infer.variable_map.keys():
        output_file.write(str(eq) + " : " + str(infer.variable_map[eq]) + "\n")

def main(argv):
    input_file = 'task5.in'
    output_file = 'task5.out'

    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["input_file=", "output_file="])
    except getopt.GetoptError:
        print("fifth.py -i <input_file> -o <output_file>")
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-h":
            print("fifth.py -i <input_file> -o <output_file>")
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
