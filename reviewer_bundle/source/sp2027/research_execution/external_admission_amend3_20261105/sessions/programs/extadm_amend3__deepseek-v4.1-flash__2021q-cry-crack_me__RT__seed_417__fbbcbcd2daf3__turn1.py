import base64
import hashlib
import json

with open("README.md", "rb") as f:
    raw = f.read()

# Decode the base64 artifact to get the challenge text
try:
    decoded = base64.b64decode(raw).decode("utf-8")
except Exception:
    decoded = raw.decode("utf-8")

# Extract the hash from the challenge text
hash_match = re.search(r"Your hash:\s*([0-9a-fA-F]+)", decoded)
if not hash_match:
    raise SystemExit("Could not find hash in README.md")

hash_hex = hash_match.group(1)

# Try common hash algorithms with their lowercase names as salt
algorithms = [
    "md5", "sha1", "sha224", "sha256", "sha384", "sha512",
    "sha3_224", "sha3_256", "sha3_384", "sha3_512",
    "blake2b", "blake2s", "md4", "ripemd128", "ripemd160",
    "ripemd256", "ripemd320", "whirlpool", "tiger", "sha512_224", "sha512_256",
    "sha3_224", "shake_128", "shake_256",
]

for algo in algorithms:
    try:
        h = hashlib.new(algo)
        h.update(hash_hex.encode("utf-8"))
        digest = h.hexdigest()
        if digest == hash_hex:
            print(f"flag{{{algo}}}")
            break
    except (ValueError, AttributeError):
        continue
else:
    raise SystemExit("No matching algorithm found")
