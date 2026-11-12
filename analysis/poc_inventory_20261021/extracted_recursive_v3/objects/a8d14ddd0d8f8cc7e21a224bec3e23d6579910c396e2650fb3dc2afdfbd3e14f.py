import sys
import json
import base64

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode ciphertexts
    ciphertexts = []
    for ct in instance['ciphertexts']:
        ciphertexts.append({
            'data': base64.b64decode(ct['data']),
            'message_index': ct['message_index']
        })
    
    # Build known plaintext map: message_index -> {offset: byte}
    known = {}
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = base64.b64decode(kp['data'])
        
        if msg_idx not in known:
            known[msg_idx] = {}
        
        for i, b in enumerate(plaintext_bytes):
            known[msg_idx][offset + i] = b
    
    # Extract target info
    target_msg = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    # Find ciphertext for target message
    target_ct = None
    for ct in ciphertexts:
        if ct['message_index'] == target_msg:
            target_ct = ct['data']
            break
    
    # Recover keystream at each position using known plaintexts
    # keystream[pos] = ciphertext[pos] ^ plaintext[pos]
    keystream = {}
    
    for msg_idx, positions in known.items():
        # Find ciphertext for this message
        msg_ct = None
        for ct in ciphertexts:
            if ct['message_index'] == msg_idx:
                msg_ct = ct['data']
                break
        
        if msg_ct is None:
            continue
        
        # Recover keystream at known positions
        for pos, plaintext_byte in positions.items():
            if pos < len(msg_ct):
                keystream[pos] = msg_ct[pos] ^ plaintext_byte
    
    # Decrypt target using recovered keystream
    result = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ct):
            plaintext_byte = target_ct[pos] ^ keystream[pos]
            result.append(plaintext_byte)
        else:
            # If we don't have keystream at this position, we can't decrypt
            result.append(0)
    
    # Convert to hex
    plaintext_hex = ''.join(f'{b:02x}' for b in result)
    
    output = {"plaintext": plaintext_hex}
    print(json.dumps(output))

if __name__ == '__main__':
    main()