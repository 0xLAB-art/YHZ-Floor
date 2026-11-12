import sys
import json

def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

def bytes_to_hex(b):
    return b.hex()

def xor_bytes(b1, b2):
    return bytes(a ^ b for a, b in zip(b1, b2))

# Read instance from command line argument
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# Extract data from instance
target = instance['target']
ciphertexts = {ct['message_index']: hex_to_bytes(ct['data']) for ct in instance['ciphertexts']}
known_plaintexts = {kp['message_index']: {'offset': kp['offset'], 'data': hex_to_bytes(kp['data'])} for kp in instance['known_plaintexts']}

# We need to recover plaintext for message at target['message_index']
target_msg_idx = target['message_index']
target_offset = target['offset']
target_length = target['length']

# Find a known plaintext we can use to recover the keystream
# Assuming message 0 has known plaintext starting at offset 0
known_msg_idx = 0
known_offset = known_plaintexts[known_msg_idx]['offset']
known_plaintext = known_plaintexts[known_msg_idx]['data']

# Get corresponding ciphertext for the known message
known_ciphertext = ciphertexts[known_msg_idx]

# Recover keystream by XORing known plaintext with its ciphertext
# keystream = plaintext XOR ciphertext
keystream_segment = xor_bytes(known_plaintext, known_ciphertext[known_offset:known_offset + len(known_plaintext)])

# Now recover the target plaintext using the keystream
target_ciphertext = ciphertexts[target_msg_idx]
target_ciphertext_segment = target_ciphertext[target_offset:target_offset + target_length]

# plaintext = ciphertext XOR keystream
recovered_plaintext = xor_bytes(target_ciphertext_segment, keystream_segment[:target_length])

# Output result
result = {
    "plaintext": bytes_to_hex(recovered_plaintext)
}
print(json.dumps(result))
