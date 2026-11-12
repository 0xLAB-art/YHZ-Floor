import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert hex ciphertexts to bytes
    ct_bytes = []
    for ct in ciphertexts:
        ct_bytes.append(bytes.fromhex(ct['data']))
    
    # This is a many-time pad attack
    # We recover the keystream from known plaintexts, then use it to decrypt the target
    
    # Build keystream from known plaintexts
    # Find the maximum offset we might need
    max_offset = target['offset'] + target['length']
    keystream = [None] * max_offset
    
    # Fill in keystream bytes from known plaintexts
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = bytes.fromhex(kp['data'])
        
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ct_bytes[msg_idx]):
                # keystream[pos] = ciphertext[pos] ^ plaintext[pos]
                ks_byte = ct_bytes[msg_idx][pos] ^ pt_byte
                if keystream[pos] is None:
                    keystream[pos] = ks_byte
                # If we already have this keystream byte, verify consistency
                elif keystream[pos] != ks_byte:
                    # Inconsistency - but let's trust the new value or keep the old
                    pass
    
    # Now decrypt the target using the recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(ct_bytes[target_msg_idx]) and keystream[pos] is not None:
            pt_byte = ct_bytes[target_msg_idx][pos] ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # If we don't have the keystream byte, we need to guess or use other techniques
            # For now, we'll use 0x00 as a placeholder (this shouldn't happen if enough known plaintexts are given)
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()