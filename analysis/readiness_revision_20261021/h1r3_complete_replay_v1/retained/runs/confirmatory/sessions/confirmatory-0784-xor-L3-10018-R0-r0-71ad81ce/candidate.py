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
    # XOR property: C1 XOR C2 = P1 XOR P2
    # If we know P1, we can find P2 = (C1 XOR C2) XOR P1
    
    # Build keystream from known plaintexts
    keystream = [None] * 300  # Allocate enough space
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_bytes = bytes.fromhex(kp['data'])
        
        # keystream[i] = ciphertext[i] XOR plaintext[i]
        for i, pt_byte in enumerate(pt_bytes):
            pos = offset + i
            ct_byte = ct_bytes[msg_idx][pos]
            keystream[pos] = ct_byte ^ pt_byte
    
    # Now decrypt the target using the recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext = []
    for i in range(target_length):
        pos = target_offset + i
        if keystream[pos] is not None:
            ct_byte = ct_bytes[target_msg_idx][pos]
            pt_byte = ct_byte ^ keystream[pos]
            plaintext.append(pt_byte)
        else:
            # Try to recover keystream from other messages
            # using crib dragging or statistical analysis
            # For now, if we don't have it, we'll need to guess
            # But given enough known plaintexts, we should have coverage
            plaintext.append(0)
    
    # Convert to hex
    plaintext_hex = bytes(plaintext).hex()
    
    print(json.dumps({"plaintext": plaintext_hex}))

if __name__ == "__main__":
    main()
