import base64
import hashlib

with open("README.md", "rb") as f:
    raw = f.read()

try:
    decoded = base64.b64decode(raw)
except Exception:
    decoded = raw

text = decoded.decode("utf-8", errors="replace")

lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

hash_line = next((ln for ln in lines if ln.lower().startswith("your hash:")), None)
salt_line = next((ln for ln in lines if ln.lower().startswith("your salt:")), None)

hash_val = None
salt_hint = None

if hash_line:
    parts = hash_line.split(":", 1)
    if len(parts) == 2:
        hash_val = parts[1].strip()

if salt_line:
    parts = salt_line.split(":", 1)
    if len(parts) == 2:
        salt_hint = parts[1].strip()

if not hash_val:
    raise SystemExit("Could not find hash in README.md")

hash_val = hash_val.lower()

if not salt_hint:
    raise SystemExit("Could not find salt hint in README.md")

salt_hint = salt_hint.lower().strip()

hashlib_names = {h.lower(): h for h in hashlib.algorithms_available}

if salt_hint in hashlib_names:
    method = hashlib_names[salt_hint]
else:
    candidates = [k for k in hashlib_names if k == salt_hint or salt_hint in k or k in salt_hint]
    if candidates:
        method = candidates[0]
    else:
        raise SystemExit(f"Unknown hash method: {salt_hint}")

print(f"flag{{{salt_hint}}}")
