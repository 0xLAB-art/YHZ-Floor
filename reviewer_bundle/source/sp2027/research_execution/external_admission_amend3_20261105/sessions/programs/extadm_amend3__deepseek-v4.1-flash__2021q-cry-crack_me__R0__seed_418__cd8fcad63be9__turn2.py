import hashlib
import string

hash_hex = "a60458d2180258d47d7f7bef5236b33e86711ac926518ca4545ebf24cdc0b76c"

# Try common hash algorithms with lowercase letters, digits, and common words
algorithms = [
    "md5", "sha1", "sha224", "sha256", "sha384", "sha512",
    "sha3_224", "sha3_256", "sha3_384", "sha3_512",
    "blake2b", "blake2s", "ripemd128", "ripemd160", "whirlpool", "tiger", "md4",
]

# Candidate word list: common words, leetspeak variants, simple patterns
words = []
for length in range(1, 13):
    for chars in [string.ascii_lowercase, string.ascii_lowercase + string.digits]:
        if length <= 4:
            continue
        # skip exhaustive for longer lengths

# Use a curated list of common words and simple patterns
candidates = []
common_words = [
    "password", "admin", "user", "login", "welcome", "hello", "secret", "test",
    "example", "letmein", "monkey", "dragon", "master", "qwerty", "abc123",
    "123456", "12345678", "123456789", "1234567890", "iloveyou", "sunshine",
    "princess", "football", "baseball", "shadow", "superman", "michael", "jennifer",
    "trustno1", "batman", "access", "flower", "cookie", "ninja", "mustang",
    "password1", "password123", "admin123", "root", "toor", "pass", "test123",
    "1234567", "1234567890123456789012345678901234567890",
    "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
    "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
    "passw0rd", "p@ssword", "password1234", "12345678901234567890123456789012345678901234567890",
]

# Add simple incremental patterns
for i in range(1, 10000):
    candidates.append(str(i))

for word in candidates:
    for algo in algorithms:
        try:
            h = hashlib.new(algo)
            h.update(word.encode())
            if h.hexdigest().lower() == hash_hex.lower():
                print(f"flag{{{word}}}")
                raise SystemExit
        except (ValueError, AttributeError):
            pass

print("Not found")
