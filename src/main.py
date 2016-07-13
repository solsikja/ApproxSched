from model import parser
from algo import cplex
import sys

if len(sys.argv) < 2:
    print("Too few arguments!")
    exit(0)

parser = parser.Parser()
parser.do(sys.argv[1] + ".tgff")
tgff = parser.generate_graphs()
# parser.info()

cplex.generate(sys.argv[1], tgff)
