import sys
import json

def hex_to_bytes(hex_string):
    return bytes.fromhex(hex_string)

def bytes_to_hex(data):
    return data.hex()

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# Extract data
ciphertexts = {ct['message_index']: hex_to_bytes(ct['data']) 
               for ct in instance['ciphertexts']}
known_plaintexts = instance['known_plaintexts']
target = instance['target']

# Recover keystream from known plaintext
# For stream cipher: ciphertext = plaintext XOR keystream
# So: keystream = plaintext XOR ciphertext
keystream = {}

for kp in known_plaintexts:
    msg_idx = kp['message_index']
    offset = kp['offset']
    plaintext = hex_to_bytes(kp['data'])
    ciphertext = ciphertexts[msg_idx]
    
    # Extract the relevant portion of ciphertext
    ct_portion = ciphertext[offset:offset + len(plaintext)]
    
    # Recover keystream for this portion
    ks_portion = xor_bytes(plaintext, ct_portion)
    
    # Store keystream by position
    if msg_idx not in keystream:
        keystream[msg_idx] = {}
    
    for i, byte in enumerate(ks_portion):
        keystream[msg_idx][offset + i] = byte

# Decrypt target using recovered keystream
target_msg_idx = target['message_index']
target_offset = target['offset']
target_length = target['length']

target_ciphertext = ciphertexts[target_msg_idx][target_offset:target_offset + target_length]

# If the same keystream is reused across messages, try using keystream from message 0
if target_msg_idx in keystream:
    ks_dict = keystream[target_msg_idx]
else:
    # Assume keystream is reused - use from message 0
    ks_dict = keystream.get(0, {})

# Build keystream bytes
plaintext_bytes = []
for i in range(target_length):
    pos = target_offset + i
    if pos in ks_dict:
        plaintext_bytes.append(target_ciphertext[i] ^ ks_dict[pos])
    else:
        # Fallback - shouldn't happen if keystream is properly recovered
        plaintext_bytes.append(0)

plaintext = bytes(plaintext_bytes)

# Output result
result = {"plaintext": bytes_to_hex(plaintext)}
print(json.dumps(result))
