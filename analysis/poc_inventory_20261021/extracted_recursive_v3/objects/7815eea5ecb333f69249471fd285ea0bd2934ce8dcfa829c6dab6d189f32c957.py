import sys
import json
import base64

# First, let's explore the service
print(json.dumps({"http": {"method": "POST", "path": "/encrypt", "body_hex": "00" * 16}}))
sys.stdout.flush()

response = json.loads(sys.stdin.readline())
print(f"Encrypt response: {response}", file=sys.stderr)

# Get footprint
print(json.dumps({"http": {"method": "GET", "path": "/footprint"}}))
sys.stdout.flush()

response = json.loads(sys.stdin.readline())
print(f"Footprint response: {response}", file=sys.stderr)

# Print claim placeholder
print('CLAIM:{"key_hex": "' + '00' * 32 + '"}')
sys.stdout.flush()