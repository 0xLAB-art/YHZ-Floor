import json
import sys

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Convert hex ciphertexts to bytes
    ct_bytes = {}
    for ct in ciphertexts:
        ct_bytes[ct['message_index']] = bytes.fromhex(ct['data'])
    
    # Build known plaintext mapping: (message_index, offset) -> plaintext_bytes
    known = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_data = bytes.fromhex(kp['data'])
        for i, byte in enumerate(pt_data):
            known[(msg_idx, offset + i)] = byte
    
    # Extract keystream bytes from known plaintexts
    # keystream[pos] = ciphertext[pos] XOR plaintext[pos]
    keystream = {}
    for (msg_idx, pos), pt_byte in known.items():
        if msg_idx in ct_bytes and pos < len(ct_bytes[msg_idx]):
            ct_byte = ct_bytes[msg_idx][pos]
            keystream[pos] = ct_byte ^ pt_byte
    
    # Decrypt target message using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    if target_msg_idx not in ct_bytes:
        result = {"plaintext": "00" * target_length}
    else:
        target_ct = ct_bytes[target_msg_idx]
        plaintext_bytes = []
        
        for i in range(target_length):
            pos = target_offset + i
            if pos in keystream and pos < len(target_ct):
                # Decrypt: plaintext = ciphertext XOR keystream
                pt_byte = target_ct[pos] ^ keystream[pos]
                plaintext_bytes.append(pt_byte)
            else:
                # Unknown byte - use 0x00 as fallback
                plaintext_bytes.append(0)
        
        plaintext_hex = bytes(plaintext_bytes).hex()
        result = {"plaintext": plaintext_hex}
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
