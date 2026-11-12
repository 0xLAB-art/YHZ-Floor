import json
import sys

def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

def bytes_to_hex(b):
    return b.hex()

def xor_bytes(b1, b2):
    return bytes(x ^ y for x, y in zip(b1, b2))

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse the instance
    ciphertexts = {ct['message_index']: hex_to_bytes(ct['data']) 
                   for ct in instance['ciphertexts']}
    
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Get the known plaintext
    known_pt = known_plaintexts[0]
    known_msg_idx = known_pt['message_index']
    known_offset = known_pt['offset']
    known_plaintext_bytes = hex_to_bytes(known_pt['data'])
    
    # Get target information
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Get the ciphertexts
    known_ciphertext = ciphertexts[known_msg_idx]
    target_ciphertext = ciphertexts[target_msg_idx]
    
    # Extract the relevant portions
    known_ct_portion = known_ciphertext[known_offset:known_offset + len(known_plaintext_bytes)]
    target_ct_portion = target_ciphertext[target_offset:target_offset + target_length]
    
    # Stream cipher attack: if C1 = P1 ⊕ K and C2 = P2 ⊕ K (same keystream K)
    # Then C1 ⊕ C2 = P1 ⊕ P2
    # So P2 = P1 ⊕ C1 ⊕ C2
    
    # Calculate the keystream from known plaintext and ciphertext
    keystream = xor_bytes(known_plaintext_bytes, known_ct_portion)
    
    # Use the keystream to decrypt the target
    # We need the keystream at the target offset
    keystream_for_target = keystream[target_offset - known_offset:target_offset - known_offset + target_length]
    
    # Decrypt target
    target_plaintext = xor_bytes(target_ct_portion, keystream_for_target)
    
    # Output result
    result = {
        "plaintext": bytes_to_hex(target_plaintext)
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()