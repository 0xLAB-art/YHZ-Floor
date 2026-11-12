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
    
    # Parse the data
    ciphertexts = {ct['message_index']: hex_to_bytes(ct['data']) 
                   for ct in instance['ciphertexts']}
    
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Get the known plaintext and corresponding ciphertext
    known_pt = known_plaintexts[0]
    known_msg_idx = known_pt['message_index']
    known_offset = known_pt['offset']
    known_plaintext_bytes = hex_to_bytes(known_pt['data'])
    
    # Get the ciphertext for the known message
    known_ciphertext = ciphertexts[known_msg_idx]
    
    # Extract the portion of ciphertext that corresponds to the known plaintext
    known_ct_portion = known_ciphertext[known_offset:known_offset + len(known_plaintext_bytes)]
    
    # Recover the keystream for this portion
    keystream = xor_bytes(known_plaintext_bytes, known_ct_portion)
    
    # Get target ciphertext
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ciphertext = ciphertexts[target_msg_idx]
    target_ct_portion = target_ciphertext[target_offset:target_offset + target_length]
    
    # Decrypt using the recovered keystream
    # Assuming the keystream is reused at the same position
    plaintext = xor_bytes(target_ct_portion, keystream[:len(target_ct_portion)])
    
    # Output result
    result = {
        "plaintext": bytes_to_hex(plaintext)
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()