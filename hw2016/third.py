import getopt
import os
import sys

from tools.tparsing import BaseParser
from tools.walgo import *


def solve(input_file, output_file):
    parser_ = BaseParser()
    walgo = WAlgorithm()
    temp = input_file.readline()

    exp = parser_.parse(temp)
    context, t = walgo.infer_type(exp)
    output_file.write(str(t) + "\n")
    for var in context.keys():
        output_file.write(str(var) + " : " + str(context[var]) + "\n")

    for eq in walgo.inst:
        output_file.write(str(eq.left) + " : " + str(eq.right) + "\n")


def main(argv):
    input_file = 'task3.in'
    output_file = 'task3.out'

    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["input_file=", "output_file="])
    except getopt.GetoptError:
        print("third.py -i <input_file> -o <output_file>")
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
