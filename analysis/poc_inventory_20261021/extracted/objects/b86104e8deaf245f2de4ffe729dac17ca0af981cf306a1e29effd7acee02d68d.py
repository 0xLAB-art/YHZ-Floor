import sys
import json

def hex_to_bytes(hex_string):
    return bytes.fromhex(hex_string)

def bytes_to_hex(byte_data):
    return byte_data.hex()

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

# Read instance from command line argument
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# Parse the instance
ciphertexts = {ct['message_index']: hex_to_bytes(ct['data']) 
               for ct in instance['ciphertexts']}
known_plaintexts = instance['known_plaintexts']
target = instance['target']

# Recover keystream from known plaintext
# We know: ciphertext = plaintext XOR keystream
# So: keystream = plaintext XOR ciphertext
keystream_segments = {}

for kp in known_plaintexts:
    msg_idx = kp['message_index']
    offset = kp['offset']
    plaintext_data = hex_to_bytes(kp['data'])
    
    ciphertext = ciphertexts[msg_idx]
    ciphertext_segment = ciphertext[offset:offset + len(plaintext_data)]
    
    # Recover keystream for this segment
    keystream = xor_bytes(plaintext_data, ciphertext_segment)
    
    if msg_idx not in keystream_segments:
        keystream_segments[msg_idx] = {}
    keystream_segments[msg_idx][offset] = keystream

# Decrypt the target
target_msg_idx = target['message_index']
target_offset = target['offset']
target_length = target['length']

target_ciphertext = ciphertexts[target_msg_idx][target_offset:target_offset + target_length]

# Find the keystream we need - check if we have it from any message at the same position
# In stream cipher reuse attacks, the same keystream is used across different messages
recovered_keystream = None

for msg_idx, segments in keystream_segments.items():
    for offset, keystream in segments.items():
        # Check if this keystream segment covers our target range
        if offset <= target_offset and offset + len(keystream) >= target_offset + target_length:
            # Extract the relevant portion
            keystream_offset = target_offset - offset
            recovered_keystream = keystream[keystream_offset:keystream_offset + target_length]
            break
    if recovered_keystream:
        break

# If keystream segments are at the same offset, they should be usable directly
if not recovered_keystream:
    # Try exact offset match (common case)
    for msg_idx, segments in keystream_segments.items():
        if target_offset in segments:
            recovered_keystream = segments[target_offset][:target_length]
            break

# Decrypt the target plaintext
plaintext = xor_bytes(target_ciphertext, recovered_keystream)

# Output result
result = {
    "plaintext": bytes_to_hex(plaintext)
}

print(json.dumps(result))
