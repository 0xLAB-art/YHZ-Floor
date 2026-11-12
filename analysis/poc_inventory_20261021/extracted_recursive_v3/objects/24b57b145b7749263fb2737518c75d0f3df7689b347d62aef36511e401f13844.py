import sys
import json

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
    
    # Parse ciphertexts
    ciphertexts = {}
    for ct in instance['ciphertexts']:
        ciphertexts[ct['message_index']] = hex_to_bytes(ct['data'])
    
    # Parse known plaintexts
    known_plaintexts = {}
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext = hex_to_bytes(kp['data'])
        if msg_idx not in known_plaintexts:
            known_plaintexts[msg_idx] = {}
        known_plaintexts[msg_idx][offset] = plaintext
    
    # Parse target
    target_msg_idx = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    # Recover keystream from known plaintext
    # Assuming the known plaintext is for message 0 at offset 0
    known_msg_idx = 0
    known_offset = 0
    known_pt = known_plaintexts[known_msg_idx][known_offset]
    known_ct = ciphertexts[known_msg_idx][known_offset:known_offset + len(known_pt)]
    
    # keystream = plaintext XOR ciphertext
    keystream = xor_bytes(known_pt, known_ct)
    
    # Decrypt target using recovered keystream
    # Assuming same keystream is used for both messages at same offset
    target_ct = ciphertexts[target_msg_idx][target_offset:target_offset + target_length]
    target_pt = xor_bytes(target_ct, keystream[:target_length])
    
    # Output result
    result = {
        "plaintext": bytes_to_hex(target_pt)
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
