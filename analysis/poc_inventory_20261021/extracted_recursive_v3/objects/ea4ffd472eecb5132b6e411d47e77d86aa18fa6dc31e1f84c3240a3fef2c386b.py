import sys
import json
import base64

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Decode all ciphertexts
    decoded_ciphertexts = {}
    for ct in ciphertexts:
        decoded_ciphertexts[ct['message_index']] = base64.b64decode(ct['data'])
    
    # Decode all known plaintexts
    known_bytes = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = base64.b64decode(kp['data'])
        
        if msg_idx not in known_bytes:
            known_bytes[msg_idx] = {}
        
        for i, byte in enumerate(plaintext_bytes):
            known_bytes[msg_idx][offset + i] = byte
    
    # Extract keystream bytes from known plaintexts
    keystream = {}
    for msg_idx in known_bytes:
        ciphertext = decoded_ciphertexts[msg_idx]
        for pos, plaintext_byte in known_bytes[msg_idx].items():
            if pos < len(ciphertext):
                keystream[pos] = ciphertext[pos] ^ plaintext_byte
    
    # Decrypt target using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ciphertext = decoded_ciphertexts[target_msg_idx]
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ciphertext):
            plaintext_byte = target_ciphertext[pos] ^ keystream[pos]
            plaintext_bytes.append(plaintext_byte)
        else:
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()