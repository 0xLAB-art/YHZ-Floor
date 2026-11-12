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
        ct_bytes.append({
            'data': bytes.fromhex(ct['data']),
            'message_index': ct['message_index']
        })
    
    # This looks like a many-time pad attack (XOR stream cipher reuse)
    # known_plaintexts gives us plaintext at specific positions for specific messages
    # We can recover keystream bytes where we have known plaintext
    
    # Recover keystream: keystream[i] = plaintext[i] ^ ciphertext[i]
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_data = bytes.fromhex(kp['data'])
        
        # Find the ciphertext for this message
        ct_data = None
        for ct in ct_bytes:
            if ct['message_index'] == msg_idx:
                ct_data = ct['data']
                break
        
        if ct_data:
            # Recover keystream bytes
            for i, pt_byte in enumerate(pt_data):
                pos = offset + i
                if pos < len(ct_data):
                    keystream[pos] = pt_byte ^ ct_data[pos]
    
    # Now decrypt the target using the recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Find target ciphertext
    target_ct = None
    for ct in ct_bytes:
        if ct['message_index'] == target_msg_idx:
            target_ct = ct['data']
            break
    
    # Decrypt target
    plaintext = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ct):
            pt_byte = target_ct[pos] ^ keystream[pos]
            plaintext.append(pt_byte)
        else:
            # If we don't have the keystream byte, we can't decrypt
            # This shouldn't happen if the problem is well-formed
            plaintext.append(0)
    
    result = {
        "plaintext": bytes(plaintext).hex()
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()