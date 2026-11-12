import sys
import json

with open(sys.argv[1], 'r') as f:
    task = json.load(f)

c1_hex = task['public_input']['c1_hex']
c2_hex = task['public_input']['c2_hex']

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

p1_xor_p2 = bytes(a ^ b for a, b in zip(c1, c2))

from itertools import product

common_words = [
    b'the ', b'and ', b'that ', b'this ', b'with ', b'from ', b'have ',
    b'for ', b'are ', b'not ', b'but ', b'was ', b'all ', b'were ',
    b'when ', b'there ', b'can ', b'said ', b'each ', b'which ',
    b'their ', b'time ', b'will ', b'way ', b'about ', b'many ',
    b'then ', b'them ', b'some ', b'her ', b'would ', b'make ',
    b'like ', b'him ', b'into ', b'could ', b'other ', b'your ',
    b'The ', b'And ', b'That ', b'This ', b'With ', b'From ',
    b' the', b' and', b' of ', b' to ', b' in ', b' is ', b' it ',
    b' a ', b' be ', b' as ', b' at ', b' so ', b' we ', b' he ',
    b' by ', b' or ', b' on ', b' do ', b' if ', b' me ', b' my ',
    b' up ', b' an ', b' go ', b' no ', b' us ', b' am '
]

best_p2 = bytearray(b' ' * 64)
best_score = -100000

for word in common_words:
    wlen = len(word)
    for start_pos in range(64 - wlen + 1):
        test_p2 = bytearray(best_p2)
        test_p2[start_pos:start_pos+wlen] = word
        
        p1_candidate = bytes(a ^ b for a, b in zip(p1_xor_p2, test_p2))
        
        score = sum(1 for b in p1_candidate if 32 <= b < 127)
        score += sum(1 for b in test_p2 if 32 <= b < 127)
        
        if score > best_score:
            best_score = score
            best_p2 = test_p2

p1 = bytes(a ^ b for a, b in zip(p1_xor_p2, best_p2))

print(f'CLAIM:{json.dumps({"plaintext2_hex": p1.hex()})}')
sys.stdout.flush()