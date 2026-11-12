import sys
import json

def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

def bytes_to_hex(b):
    return b.hex()

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Find the known plaintext for message 0
    known_pt = None
    for kp in known_plaintexts:
        if kp['message_index'] == 0:
            known_pt = kp
            break
    
    # Find ciphertext for message 0
    ct_msg_0 = None
    for ct in ciphertexts:
        if ct['message_index'] == 0:
            ct_msg_0 = ct
            break
    
    # Find ciphertext for target message
    ct_target = None
    for ct in ciphertexts:
        if ct['message_index'] == target['message_index']:
            ct_target = ct
            break
    
    # Extract keystream from known plaintext and ciphertext
    # keystream = plaintext XOR ciphertext
    plaintext_0 = hex_to_bytes(known_pt['data'])
    ciphertext_0 = hex_to_bytes(ct_msg_0['data'])
    keystream = xor_bytes(plaintext_0, ciphertext_0)
    
    # Decrypt target message using the keystream
    # plaintext = ciphertext XOR keystream
    ciphertext_target = hex_to_bytes(ct_target['data'])
    
    # Extract the portion we need based on offset and length
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext_target = xor_bytes(ciphertext_target, keystream)
    plaintext_extract = plaintext_target[target_offset:target_offset + target_length]
    
    result = {
        "plaintext": bytes_to_hex(plaintext_extract)
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
