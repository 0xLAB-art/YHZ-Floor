import sys
import json

def main():
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
    # For each position, we can recover the keystream if we have a known plaintext
    max_len = max(len(ct) for ct in ct_bytes)
    keystream = [None] * max_len
    
    # Extract keystream from known plaintexts
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_data = bytes.fromhex(kp['data'])
        ct = ct_bytes[msg_idx]
        
        for i, pt_byte in enumerate(pt_data):
            pos = offset + i
            if pos < len(ct):
                keystream[pos] = ct[pos] ^ pt_byte
    
    # Now decrypt the target using the recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ct = ct_bytes[target_msg_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(target_ct) and keystream[pos] is not None:
            plaintext_bytes.append(target_ct[pos] ^ keystream[pos])
        else:
            # If we don't have the keystream, we can't decrypt
            # This shouldn't happen with the given instance
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()