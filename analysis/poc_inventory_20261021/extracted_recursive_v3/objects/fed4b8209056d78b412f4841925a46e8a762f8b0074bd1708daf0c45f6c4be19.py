import sys
import json

def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

def bytes_to_hex(b):
    return b.hex()

def xor_bytes(b1, b2):
    return bytes(x ^ y for x, y in zip(b1, b2))

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

ciphertexts = [hex_to_bytes(ct['data']) for ct in instance['ciphertexts']]
known_plaintexts = instance['known_plaintexts']
target = instance['target']

# Recover keystream from known plaintexts
# keystream[i] = plaintext[i] XOR ciphertext[i]
max_len = max(len(ct) for ct in ciphertexts)
keystream = [None] * max_len

for kp in known_plaintexts:
    msg_idx = kp['message_index']
    offset = kp['offset']
    plaintext_bytes = hex_to_bytes(kp['data'])
    
    for i, pt_byte in enumerate(plaintext_bytes):
        pos = offset + i
        ct_byte = ciphertexts[msg_idx][pos]
        key_byte = pt_byte ^ ct_byte
        
        # Verify consistency if we already have this keystream byte
        if keystream[pos] is not None:
            if keystream[pos] != key_byte:
                # Inconsistency detected - but shouldn't happen in valid instance
                pass
        keystream[pos] = key_byte

# Decrypt target using recovered keystream
target_msg_idx = target['message_index']
target_offset = target['offset']
target_length = target['length']

result_bytes = []
for i in range(target_length):
    pos = target_offset + i
    if pos < len(ciphertexts[target_msg_idx]) and keystream[pos] is not None:
        ct_byte = ciphertexts[target_msg_idx][pos]
        pt_byte = ct_byte ^ keystream[pos]
        result_bytes.append(pt_byte)
    else:
        # If we don't have the keystream byte, we need to try to infer it
        # For now, this shouldn't happen if the instance is solvable
        result_bytes.append(0)

plaintext_hex = bytes_to_hex(bytes(result_bytes))

output = {"plaintext": plaintext_hex}
print(json.dumps(output))