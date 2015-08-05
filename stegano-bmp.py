import argparse

parser = argparse.ArgumentParser()

parser.add_argument("sourcefile")
parser.add_argument("result")
parser.add_argument("message")

args = parser.parse_args()