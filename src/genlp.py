#!/usr/bin/python3.5

from model import tgffparser
from algo import general
from algo import approxsched
from algo import approxsched_without_slack
import sys

if len(sys.argv) < 2:
    print("Too few arguments!")
    exit(0)

tgff_parser = tgffparser.TgffParser()
tgff_parser.do(sys.argv[1] + ".tgff")
tgff = tgff_parser.generate_graphs()
# tgff_parser.info()

# general.generate(sys.argv[1], tgff)
# approxsched_without_slack.generate(sys.argv[1], tgff)
approxsched.generate(sys.argv[1], tgff)
