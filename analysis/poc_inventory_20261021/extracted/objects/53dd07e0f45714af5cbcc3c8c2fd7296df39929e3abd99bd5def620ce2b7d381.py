import json
import sys

inst = json.loads(sys.stdin.read())
sys.stderr.write('no stdout output was produced')
