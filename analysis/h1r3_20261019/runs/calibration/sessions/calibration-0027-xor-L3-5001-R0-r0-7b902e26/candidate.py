import json
import sys

def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

def bytes_to_hex(b):
    return b.hex()

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = {}
    for ct in instance['ciphertexts']:
        msg_idx = ct['message_index']
        ciphertexts[msg_idx] = hex_to_bytes(ct['data'])
    
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    keystream = {}
    
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = hex_to_bytes(kp['data'])
        ciphertext = ciphertexts[msg_idx]
        
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            ct_byte = ciphertext[pos]
            ks_byte = ct_byte ^ pt_byte
            keystream[pos] = ks_byte
    
    target_ciphertext = ciphertexts[target_msg_idx]
    plaintext = bytearray(target_length)
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            plaintext[i] = target_ciphertext[pos] ^ keystream[pos]
        else:
            plaintext[i] = 0
    
    result = {
        "plaintext": bytes_to_hex(plaintext)
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
