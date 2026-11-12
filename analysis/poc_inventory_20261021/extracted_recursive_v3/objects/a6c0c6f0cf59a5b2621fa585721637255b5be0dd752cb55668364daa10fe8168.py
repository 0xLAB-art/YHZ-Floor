import sys
import json

def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

def bytes_to_hex(b):
    return b.hex()

def xor_bytes(b1, b2):
    return bytes(a ^ b for a, b in zip(b1, b2))

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = {}
    for ct in instance['ciphertexts']:
        ciphertexts[ct['message_index']] = hex_to_bytes(ct['data'])
    
    known_plaintexts = {}
    for kp in instance['known_plaintexts']:
        key = (kp['message_index'], kp['offset'])
        known_plaintexts[key] = hex_to_bytes(kp['data'])
    
    target = instance['target']
    target_length = target['length']
    target_message_index = target['message_index']
    target_offset = target['offset']
    
    known_pt = known_plaintexts[(0, 0)]
    known_ct = ciphertexts[0][0:len(known_pt)]
    
    keystream = xor_bytes(known_pt, known_ct)
    
    target_ct = ciphertexts[target_message_index][target_offset:target_offset + target_length]
    
    plaintext = xor_bytes(target_ct, keystream[:target_length])
    
    result = {
        "plaintext": bytes_to_hex(plaintext)
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()