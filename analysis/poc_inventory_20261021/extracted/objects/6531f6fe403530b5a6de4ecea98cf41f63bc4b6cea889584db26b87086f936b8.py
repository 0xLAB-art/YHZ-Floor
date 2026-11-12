import json
import sys

def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

def bytes_to_hex(b):
    return b.hex()

def xor_bytes(b1, b2):
    return bytes(a ^ b for a, b in zip(b1, b2))

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse the instance
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Get ciphertexts
    ciphertexts = {}
    for ct in instance['ciphertexts']:
        ciphertexts[ct['message_index']] = hex_to_bytes(ct['data'])
    
    # Get known plaintexts
    known_plaintexts = {}
    for kp in instance['known_plaintexts']:
        if kp['message_index'] not in known_plaintexts:
            known_plaintexts[kp['message_index']] = {}
        known_plaintexts[kp['message_index']][kp['offset']] = hex_to_bytes(kp['data'])
    
    # We have ciphertext for message 0 and 1
    # We have plaintext for message 0
    # We need plaintext for message 1
    
    c0 = ciphertexts[0]
    c1 = ciphertexts[target_msg_idx]
    p0 = known_plaintexts[0][0]
    
    # Stream cipher with key reuse: C = P ⊕ K
    # C0 = P0 ⊕ K
    # C1 = P1 ⊕ K
    # Therefore: C0 ⊕ C1 = P0 ⊕ P1
    # So: P1 = P0 ⊕ C0 ⊕ C1
    
    # Extract the target portion
    end_offset = target_offset + target_length
    c0_portion = c0[target_offset:end_offset]
    c1_portion = c1[target_offset:end_offset]
    p0_portion = p0[target_offset:end_offset]
    
    # Recover P1
    p1_portion = xor_bytes(xor_bytes(p0_portion, c0_portion), c1_portion)
    
    # Output result
    result = {
        "plaintext": bytes_to_hex(p1_portion)
    }
    print(json.dumps(result))

if __name__ == '__main__':
    main()
