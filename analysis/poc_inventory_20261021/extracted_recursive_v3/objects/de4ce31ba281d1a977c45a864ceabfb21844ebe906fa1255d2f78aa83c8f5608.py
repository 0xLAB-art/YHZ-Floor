import sys
import json

def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

def bytes_to_hex(b):
    return b.hex()

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse input
    ciphertexts = {ct['message_index']: hex_to_bytes(ct['data']) 
                   for ct in instance['ciphertexts']}
    
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Get the known plaintext
    known = known_plaintexts[0]
    known_msg_idx = known['message_index']
    known_offset = known['offset']
    known_plaintext = hex_to_bytes(known['data'])
    known_length = len(known_plaintext)
    
    # Get target info
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Extract the relevant portions of ciphertexts
    c_known = ciphertexts[known_msg_idx][known_offset:known_offset + known_length]
    c_target = ciphertexts[target_msg_idx][target_offset:target_offset + target_length]
    
    # Recover the keystream for the known plaintext region
    # K = P ⊕ C (for the known plaintext)
    keystream = xor_bytes(known_plaintext, c_known)
    
    # Now decrypt the target using the recovered keystream
    # If the same keystream was used at the same offset:
    # P_target = C_target ⊕ K
    
    # Check if we have enough keystream
    min_length = min(len(keystream), len(c_target))
    target_plaintext = xor_bytes(c_target[:min_length], keystream[:min_length])
    
    # Output result
    result = {
        "plaintext": bytes_to_hex(target_plaintext)
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()