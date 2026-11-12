import sys
import json

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert hex ciphertext strings to byte arrays
    ct_bytes = []
    for ct in ciphertexts:
        ct_bytes.append(bytes.fromhex(ct['data']))
    
    # This is a many-time pad attack
    # XOR property: if C1 = P1 XOR K and C2 = P2 XOR K
    # then C1 XOR C2 = P1 XOR P2
    # and if we know P1, we can recover P2 = P1 XOR C1 XOR C2
    
    # First, recover the keystream at positions where we have known plaintexts
    max_len = max(len(ct) for ct in ct_bytes)
    keystream = [None] * max_len
    
    # For each known plaintext, recover the keystream at those positions
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = bytes.fromhex(kp['data'])
        
        ct = ct_bytes[msg_idx]
        
        for i, p_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ct):
                # K = P XOR C
                k_byte = p_byte ^ ct[pos]
                if keystream[pos] is None:
                    keystream[pos] = k_byte
                # Verify consistency if we already recovered this keystream byte
                elif keystream[pos] != k_byte:
                    # There's an inconsistency - should not happen with correct data
                    pass
    
    # Now decrypt the target message using the recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ct = ct_bytes[target_msg_idx]
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(target_ct) and keystream[pos] is not None:
            # P = C XOR K
            p_byte = target_ct[pos] ^ keystream[pos]
            plaintext_bytes.append(p_byte)
        else:
            # We don't have the keystream at this position
            # This should not happen if the challenge is solvable
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
