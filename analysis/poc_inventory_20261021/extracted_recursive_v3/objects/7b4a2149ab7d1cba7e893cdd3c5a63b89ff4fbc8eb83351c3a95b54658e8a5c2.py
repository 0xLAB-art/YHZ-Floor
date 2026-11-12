import sys
import json
import base64

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse the instance
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Decode ciphertexts
    ct_map = {}
    for ct in ciphertexts:
        ct_map[ct['message_index']] = base64.b64decode(ct['data'])
    
    # Decode known plaintexts
    kp_map = {}
    for kp in known_plaintexts:
        if kp['message_index'] not in kp_map:
            kp_map[kp['message_index']] = {}
        kp_map[kp['message_index']][kp['offset']] = base64.b64decode(kp['data'])
    
    # Recover keystream from known plaintext
    # For stream cipher: ciphertext = plaintext XOR keystream
    # Therefore: keystream = plaintext XOR ciphertext
    keystream = bytearray()
    
    # Use the known plaintext at message_index 0, offset 0
    known_msg_idx = 0
    known_offset = 0
    known_pt = kp_map[known_msg_idx][known_offset]
    known_ct = ct_map[known_msg_idx]
    
    # Recover keystream starting from known_offset
    for i in range(len(known_pt)):
        keystream.append(known_pt[i] ^ known_ct[known_offset + i])
    
    # Now decrypt the target using the recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ct = ct_map[target_msg_idx]
    
    # Decrypt: plaintext = ciphertext XOR keystream
    plaintext = bytearray()
    for i in range(target_length):
        ct_byte = target_ct[target_offset + i]
        # The keystream position corresponds to the position in the message
        ks_byte = keystream[i]
        plaintext.append(ct_byte ^ ks_byte)
    
    # Convert to hex
    plaintext_hex = plaintext.hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()