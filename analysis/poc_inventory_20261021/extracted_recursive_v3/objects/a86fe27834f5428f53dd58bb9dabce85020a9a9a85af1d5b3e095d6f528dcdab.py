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
    
    # Extract known plaintext information
    known_pt = known_plaintexts[0]
    known_msg_idx = known_pt['message_index']
    known_offset = known_pt['offset']
    known_pt_data = hex_to_bytes(known_pt['data'])
    
    # Get the corresponding ciphertext
    known_ct = ciphertexts[known_msg_idx]
    known_ct_segment = known_ct[known_offset:known_offset + len(known_pt_data)]
    
    # Recover keystream: keystream = plaintext XOR ciphertext
    keystream = xor_bytes(known_pt_data, known_ct_segment)
    
    # Now decrypt the target using the recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ct = ciphertexts[target_msg_idx]
    target_ct_segment = target_ct[target_offset:target_offset + target_length]
    
    # Decrypt: plaintext = ciphertext XOR keystream
    # We need to use the keystream starting from the target offset
    keystream_segment = keystream[target_offset:target_offset + target_length]
    plaintext = xor_bytes(target_ct_segment, keystream_segment)
    
    # Output result
    result = {"plaintext": bytes_to_hex(plaintext)}
    print(json.dumps(result))

if __name__ == "__main__":
    main()