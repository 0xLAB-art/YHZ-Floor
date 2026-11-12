import sys
import json
import base64

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode ciphertexts
    ciphertexts = []
    for ct in instance['ciphertexts']:
        data = base64.b64decode(ct['data'])
        ciphertexts.append({
            'data': data,
            'message_index': ct['message_index']
        })
    
    # Build keystream from known plaintexts
    # keystream[message_index][offset] = keystream_byte
    keystream = {}
    
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = base64.b64decode(kp['data'])
        
        if msg_idx not in keystream:
            keystream[msg_idx] = {}
        
        # Get corresponding ciphertext
        ct_data = None
        for ct in ciphertexts:
            if ct['message_index'] == msg_idx:
                ct_data = ct['data']
                break
        
        # Recover keystream: keystream = plaintext XOR ciphertext
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ct_data):
                ks_byte = pt_byte ^ ct_data[pos]
                keystream[msg_idx][pos] = ks_byte
    
    # Extract target
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Get target ciphertext
    target_ct = None
    for ct in ciphertexts:
        if ct['message_index'] == target_msg_idx:
            target_ct = ct['data']
            break
    
    # Try to decrypt target using keystream from any message
    # In many stream cipher attacks, the same keystream is reused across messages
    # Let's try to find keystream bytes at the target positions
    
    # First, check if we have keystream for the target message itself
    plaintext_bytes = []
    
    # Strategy: assume keystream is reused across all messages at the same offset
    for i in range(target_length):
        pos = target_offset + i
        
        # Try to find keystream at this position from any message
        ks_byte = None
        
        # First try the target message itself
        if target_msg_idx in keystream and pos in keystream[target_msg_idx]:
            ks_byte = keystream[target_msg_idx][pos]
        else:
            # Try other messages (assuming keystream reuse)
            for msg_idx in keystream:
                if pos in keystream[msg_idx]:
                    ks_byte = keystream[msg_idx][pos]
                    break
        
        if ks_byte is not None and pos < len(target_ct):
            pt_byte = target_ct[pos] ^ ks_byte
            plaintext_bytes.append(pt_byte)
        else:
            # No keystream available - this shouldn't happen if puzzle is solvable
            plaintext_bytes.append(0)
    
    # Convert to hex
    plaintext_hex = ''.join(f'{b:02x}' for b in plaintext_bytes)
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
