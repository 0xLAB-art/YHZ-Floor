import sys
import json

def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

def bytes_to_hex(b):
    return b.hex()

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = {ct['message_index']: hex_to_bytes(ct['data']) 
                   for ct in instance['ciphertexts']}
    
    known = instance['known_plaintexts'][0]
    known_plaintext = hex_to_bytes(known['data'])
    known_message_idx = known['message_index']
    known_offset = known['offset']
    
    target = instance['target']
    target_message_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    known_ciphertext = ciphertexts[known_message_idx]
    known_ct_segment = known_ciphertext[known_offset:known_offset + len(known_plaintext)]
    
    keystream = xor_bytes(known_plaintext, known_ct_segment)
    
    target_ciphertext = ciphertexts[target_message_idx]
    target_ct_segment = target_ciphertext[target_offset:target_offset + target_length]
    
    target_plaintext = xor_bytes(target_ct_segment, keystream[:len(target_ct_segment)])
    
    result = {
        "plaintext": bytes_to_hex(target_plaintext)
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()