import sys, json, base64, hashlib, secrets

# First, let's explore the HTTP endpoint to understand the SSH service interface
print(json.dumps({"http": {"method": "GET", "path": "/"}}), flush=True)

# Read the response
response = json.loads(sys.stdin.readline())
print(f"Response: {response}", file=sys.stderr)