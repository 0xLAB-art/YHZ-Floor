"""
ACTS-Attack E2A scripted producer program.
"""
import json
import sys


def main():
    with open(sys.argv[1], "r", encoding="utf-8") as handle:
        instance = json.load(handle)
    raise SystemExit(3)


main()
