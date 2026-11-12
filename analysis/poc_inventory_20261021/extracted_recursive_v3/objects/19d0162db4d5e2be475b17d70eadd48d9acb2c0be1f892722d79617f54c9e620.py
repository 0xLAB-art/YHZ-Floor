import sys
import json
import base64

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode all ciphertexts from base64
    ciphertexts = []
    for ct in instance['ciphertexts']:
        ciphertexts.append({
            'data': base64.b64decode(ct['data']),
            'message_index': ct['message_index']
        })
    
    # Decode known plaintexts
    known_plaintexts = []
    for kp in instance['known_plaintexts']:
        known_plaintexts.append({
            'data': base64.b64decode(kp['data']),
            'message_index': kp['message_index'],
            'offset': kp['offset']
        })
    
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Create ciphertext lookup by message index
    ct_by_idx = {}
    for ct in ciphertexts:
        ct_by_idx[ct['message_index']] = ct['data']
    
    # This is a many-time pad attack
    # When the same key is reused: C1 XOR C2 = P1 XOR P2
    # If we know P1, we can find P2 = (C1 XOR C2) XOR P1
    
    # Build keystream from known plaintexts
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = kp['data']
        
        if msg_idx in ct_by_idx:
            ciphertext = ct_by_idx[msg_idx]
            for i, pt_byte in enumerate(plaintext_bytes):
                pos = offset + i
                if pos < len(ciphertext):
                    key_byte = ciphertext[pos] ^ pt_byte
                    keystream[pos] = key_byte
    
    # Now decrypt the target using the recovered keystream
    target_ciphertext = ct_by_idx[target_msg_idx]
    plaintext = bytearray(target_length)
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ciphertext):
            plaintext[i] = target_ciphertext[pos] ^ keystream[pos]
        else:
            # If we don't have the keystream byte, we need to derive it
            # Try to find it from other known plaintexts at the same position
            plaintext[i] = 0
    
    # Output the result
    result = {
        "plaintext": plaintext.hex()
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()