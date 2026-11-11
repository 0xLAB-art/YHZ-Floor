import base64

with open("ciphertext.txt", "rb") as f:
    data = f.read()

cipher = base64.b64decode(data).decode("utf-8")

# The puzzle: "yeeeeeeeeeeeeeeeeeeeeeeeeeeeeeet single yeet yeeted with single yeet == 0 yeeet what is yeet?"
# Count the 'e's in "yeeeeeeeeeeeeeeeeeeeeeeeeeeeeeet": 29 e's
# "single yeet" = 1
# "yeeted with single yeet" = 1
# The pattern: count of 'e' characters determines the answer.
# "yeeeeeeeeeeeeeeeeeeeeeeeeeeeeeet" has 29 e's -> the answer is the 29th letter of the alphabet = 'c'
# But let's verify by counting e's in the string.

e_count = cipher.count("e")

# The flag format is typically a single character or short string.
# Given the riddle structure, the answer is the letter at position e_count in the alphabet.
flag = chr(ord("a") + e_count - 1)

print(flag)
