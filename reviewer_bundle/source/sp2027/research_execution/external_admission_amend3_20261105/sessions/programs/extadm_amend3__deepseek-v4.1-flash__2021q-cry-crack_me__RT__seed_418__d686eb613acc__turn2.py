import base64
import hashlib

with open("README.md", "rb") as f:
    raw = f.read()

try:
    decoded = base64.b64decode(raw)
except Exception:
    decoded = raw

text = decoded.decode("utf-8", errors="replace")

hash_line = None
for line in text.splitlines():
    if line.startswith("Your hash:"):
        hash_line = line
        break

if hash_line is None:
    raise SystemExit("No hash line found")

hash_value = hash_line.split(":", 1)[1].strip()

# Candidate hash algorithms to try
algorithms = [
    "md5", "sha1", "sha224", "sha256", "sha384", "sha512",
    "sha3_224", "sha3_256", "sha3_384", "sha3_512",
    "blake2b", "blake2s", "md4", "ripemd128", "ripemd160",
    "whirlpool", "tiger", "gost", "shake_128", "shake_256",
]

# Common single-word dictionary candidates
words = []
with open("words.txt", "r", errors="replace") as f:
    words.extend(w.strip().lower() for w in f if w.strip())

# Also include common CTF-style words
common_words = [
    "flag", "password", "secret", "admin", "root", "test", "example",
    "letmein", "welcome", "monkey", "dragon", "master", "qwerty",
    "login", "pass", "123456", "12345678", "abc123", "iloveyou",
    "princess", "sunshine", "football", "baseball", "superman",
    "trustno1", "shadow", "michael", "jennifer", "hunter", "access",
    "hello", "charlie", "donald", "passw0rd", "qwerty123", "admin123",
    "1234567", "12345", "1234", "123456789", "1234567890",
]
words.extend(common_words)

# Deduplicate while preserving order
seen = set()
unique_words = []
for w in words:
    if w not in seen and len(w) > 0:
        seen.add(w)
        unique_words.append(w)

found = None

# Try each algorithm with each word
for algo in algorithms:
    try:
        h = hashlib.new(algo)
    except ValueError:
        continue
    for word in unique_words:
        h.update(word.encode("utf-8"))
        if h.hexdigest() == hash_value:
            found = word
            break
    if found:
        break

if found is None:
    raise SystemExit("No match found")

print(f"flag{{{found}}}")
