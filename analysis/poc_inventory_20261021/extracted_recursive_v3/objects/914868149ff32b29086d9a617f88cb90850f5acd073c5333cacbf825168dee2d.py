import sys
import json

with open(sys.argv[1], 'r') as f:
    task = json.load(f)

c1_hex = task['public_input']['c1_hex']
c2_hex = task['public_input']['c2_hex']

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

p1_xor_p2 = bytes(a ^ b for a, b in zip(c1, c2))

common_bytes = [
    b' ', b'e', b't', b'a', b'o', b'i', b'n', b's', b'h', b'r',
    b'd', b'l', b'c', b'u', b'm', b'w', b'f', b'g', b'y', b'p',
    b'b', b'v', b'k', b'j', b'x', b'q', b'z',
    b'E', b'T', b'A', b'O', b'I', b'N', b'S', b'H', b'R',
    b'0', b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9',
    b'.', b',', b'!', b'?', b'\n', b'\r', b'-', b'_', b'/', b':'
]

def score_as_p2(byte_val):
    if 97 <= byte_val <= 122:
        return 10
    elif byte_val == 32:
        return 8
    elif 65 <= byte_val <= 90:
        return 7
    elif 48 <= byte_val <= 57:
        return 5
    elif byte_val in [46, 44, 10, 13, 45, 95]:
        return 3
    elif 32 <= byte_val < 127:
        return 1
    else:
        return -10

p2_guess = bytearray(64)
for i in range(64):
    xor_val = p1_xor_p2[i]
    best_score = -1000
    best_byte = 32
    
    for candidate in range(256):
        p1_byte = xor_val ^ candidate
        score = score_as_p2(candidate) + score_as_p2(p1_byte)
        if score > best_score:
            best_score = score
            best_byte = candidate
    
    p2_guess[i] = best_byte

p1 = bytes(a ^ b for a, b in zip(p1_xor_p2, p2_guess))

print(f'CLAIM:{json.dumps({"plaintext2_hex": p1.hex()})}')
sys.stdout.flush()