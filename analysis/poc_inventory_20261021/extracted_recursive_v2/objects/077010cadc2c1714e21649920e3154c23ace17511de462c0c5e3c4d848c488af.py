import json
import sys

inst = json.loads(sys.stdin.read())
print('ECHO not a json object')
