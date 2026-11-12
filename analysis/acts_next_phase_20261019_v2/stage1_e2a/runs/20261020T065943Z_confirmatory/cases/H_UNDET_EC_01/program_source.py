"""
ACTS-Attack E2A scripted producer program.
"""
import json
import sys


def main():
    with open(sys.argv[1], "r", encoding="utf-8") as handle:
        instance = json.load(handle)
    print(json.dumps({"status": "UNDERDETERMINED",
                      "reason": "the public instance does not determine a unique target"},
                     sort_keys=True))


main()
