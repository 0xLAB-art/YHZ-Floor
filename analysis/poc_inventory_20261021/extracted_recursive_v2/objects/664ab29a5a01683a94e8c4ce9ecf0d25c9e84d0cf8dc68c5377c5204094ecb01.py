"""
ACTS-Attack E2A scripted producer program.
"""
import json
import sys


def main():
    with open(sys.argv[1], "r", encoding="utf-8") as handle:
        instance = json.load(handle)
    sys.stdout.write("result: not-a-json-document {\n")
    sys.stdout.flush()


main()
