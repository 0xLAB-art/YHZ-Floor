import json
import sys

def hex_to_bytes(hex_string):
    return bytes.fromhex(hex_string)

def bytes_to_hex(byte_data):
    return byte_data.hex()

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse the instance
    ciphertexts = {ct['message_index']: hex_to_bytes(ct['data']) 
                   for ct in instance['ciphertexts']}
    
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Recover keystream from known plaintext
    # For each known plaintext, we can recover the keystream at those positions
    keystreams = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        known_pt = hex_to_bytes(kp['data'])
        
        # Get the corresponding ciphertext portion
        ct = ciphertexts[msg_idx]
        ct_portion = ct[offset:offset + len(known_pt)]
        
        # Recover keystream: keystream = plaintext XOR ciphertext
        keystream = xor_bytes(known_pt, ct_portion)
        
        if msg_idx not in keystreams:
            keystreams[msg_idx] = {}
        keystreams[msg_idx][offset] = keystream
    
    # Now decrypt the target using the recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Get target ciphertext
    target_ct = ciphertexts[target_msg_idx][target_offset:target_offset + target_length]
    
    # Try to decrypt using keystream from the same message or other messages
    # First, check if we have keystream for the target message at the right offset
    plaintext = None
    
    # Check if keystream was recovered from the same position
    if target_msg_idx in keystreams and target_offset in keystreams[target_msg_idx]:
        keystream = keystreams[target_msg_idx][target_offset]
        plaintext = xor_bytes(target_ct, keystream[:target_length])
    else:
        # Try keystream from other messages at the same offset (keystream reuse)
        for msg_idx in keystreams:
            if target_offset in keystreams[msg_idx]:
                keystream = keystreams[msg_idx][target_offset]
                plaintext = xor_bytes(target_ct, keystream[:target_length])
                break
    
    # Output result
    result = {
        "plaintext": bytes_to_hex(plaintext)
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()