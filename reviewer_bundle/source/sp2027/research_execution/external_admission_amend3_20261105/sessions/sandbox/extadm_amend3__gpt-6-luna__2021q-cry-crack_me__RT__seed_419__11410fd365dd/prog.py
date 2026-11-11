import base64
import hashlib
import json
import os
import re

# Read README.md from working directory
with open('README.md', 'rb') as f:
    raw = f.read()

# Decode base64 artifact to get the challenge text
text = base64.b64decode(raw).decode('utf-8')

# Extract the hash from the challenge text
hash_match = re.search(r'Your hash:\s*([a-f0-9]+)', text, re.IGNORECASE)
assert hash_match, 'Could not find hash in README.md'
hash_hex = hash_match.group(1)

# Extract the salt (encryption method) from the challenge text
salt_match = re.search(r'Your salt:\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
assert salt_match, 'Could not find salt in README.md'
salt = salt_match.group(1).strip()

# Compute the hash with the given salt as the method name
try:
    h = hashlib.new(salt, hash_hex.encode('utf-8'))
    result = h.hexdigest()
except ValueError as e:
    raise SystemExit(f'Invalid hash method: {salt}')

# Print the flag
print(f'flag{{{result}}}')
