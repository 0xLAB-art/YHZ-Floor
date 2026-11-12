import sys
import json
import base64

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode all ciphertexts
    ciphertexts = []
    for ct in instance['ciphertexts']:
        ciphertexts.append(base64.b64decode(ct['data']))
    
    # Build known plaintext map: message_index -> {offset -> byte_value}
    known = {}
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = base64.b64decode(kp['data'])
        
        if msg_idx not in known:
            known[msg_idx] = {}
        
        for i, byte in enumerate(plaintext_bytes):
            known[msg_idx][offset + i] = byte
    
    # Extract keystream from known plaintexts
    # keystream[position] = key_byte at that position
    keystream = {}
    
    for msg_idx, positions in known.items():
        ciphertext = ciphertexts[msg_idx]
        for pos, plaintext_byte in positions.items():
            if pos < len(ciphertext):
                key_byte = ciphertext[pos] ^ plaintext_byte
                keystream[pos] = key_byte
    
    # Decrypt the target
    target_msg_idx = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    target_ciphertext = ciphertexts[target_msg_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ciphertext):
            plaintext_byte = target_ciphertext[pos] ^ keystream[pos]
            plaintext_bytes.append(plaintext_byte)
        else:
            # Should not happen if we have enough known plaintext
            plaintext_bytes.append(0)
    
    # Convert to hex
    plaintext_hex = ''.join(f'{b:02x}' for b in plaintext_bytes)
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()