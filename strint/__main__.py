import argparse
from . import strint


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("numeric_string", nargs="+")
    args = parser.parse_args()
    print(strint(" ".join(args.numeric_string)))


main()
