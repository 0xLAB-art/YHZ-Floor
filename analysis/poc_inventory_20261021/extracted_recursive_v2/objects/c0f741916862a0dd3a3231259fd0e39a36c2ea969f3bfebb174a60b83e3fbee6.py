import sys
import json

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert hex ciphertexts to bytes
    ct_bytes = []
    for ct in ciphertexts:
        ct_bytes.append(bytes.fromhex(ct['data']))
    
    # This is a many-time pad attack
    # XOR of two ciphertexts gives XOR of two plaintexts: C1 XOR C2 = (P1 XOR K) XOR (P2 XOR K) = P1 XOR P2
    # If we know P1, we can recover P2
    
    # Build a keystream recovery map
    keystream = {}
    
    # For each known plaintext, recover the keystream at those positions
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = bytes.fromhex(kp['data'])
        
        for i, pb in enumerate(plaintext_bytes):
            pos = offset + i
            # keystream[pos] = ciphertext[pos] XOR plaintext[pos]
            kb = ct_bytes[msg_idx][pos] ^ pb
            keystream[pos] = kb
    
    # Now recover the target plaintext
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            # Decrypt: plaintext = ciphertext XOR keystream
            pt_byte = ct_bytes[target_msg_idx][pos] ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # We don't have the keystream for this position
            # Try to recover it from other messages using crib dragging
            # For now, we'll use 0x00 as a placeholder (this shouldn't happen if properly constructed)
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
