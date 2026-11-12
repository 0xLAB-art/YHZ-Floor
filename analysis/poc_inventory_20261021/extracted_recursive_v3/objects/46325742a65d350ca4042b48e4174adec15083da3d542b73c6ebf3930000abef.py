import sys
import json

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    # Parse input
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert hex ciphertexts to bytes
    ct_bytes = []
    for ct in ciphertexts:
        ct_bytes.append(bytes.fromhex(ct['data']))
    
    # This is a many-time pad attack
    # XOR property: C = P ^ K, so P = C ^ K
    # If we know plaintext at position i: K[i] = C[i] ^ P[i]
    
    # Recover keystream bytes from known plaintexts
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_hex = kp['data']
        pt_bytes = bytes.fromhex(pt_hex)
        
        # Recover keystream: K = C ^ P
        for i, pt_byte in enumerate(pt_bytes):
            pos = offset + i
            ct_byte = ct_bytes[msg_idx][pos]
            k_byte = ct_byte ^ pt_byte
            keystream[pos] = k_byte
    
    # Now decrypt the target using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            # Decrypt: P = C ^ K
            ct_byte = ct_bytes[target_msg_idx][pos]
            pt_byte = ct_byte ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # If keystream not known at this position, we have a problem
            # This shouldn't happen given the problem structure
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()