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
    
    # Find the ciphertext and known plaintext for message 0
    ct0 = None
    pt0 = None
    
    for ct in ciphertexts:
        if ct['message_index'] == 0:
            ct0 = hex_to_bytes(ct['data'])
            break
    
    for kp in known_plaintexts:
        if kp['message_index'] == 0:
            pt0_offset = kp['offset']
            pt0 = hex_to_bytes(kp['data'])
            break
    
    # Find the ciphertext for the target message
    ct1 = None
    for ct in ciphertexts:
        if ct['message_index'] == target['message_index']:
            ct1 = hex_to_bytes(ct['data'])
            break
    
    # Recover the keystream from message 0
    # keystream = ciphertext_0 XOR plaintext_0
    keystream = xor_bytes(ct0[pt0_offset:pt0_offset + len(pt0)], pt0)
    
    # Decrypt the target portion of message 1
    # plaintext_1 = ciphertext_1 XOR keystream
    target_offset = target['offset']
    target_length = target['length']
    
    # Extract the relevant portion of ciphertext and keystream
    ct1_portion = ct1[target_offset:target_offset + target_length]
    keystream_portion = keystream[target_offset:target_offset + target_length]
    
    pt1_portion = xor_bytes(ct1_portion, keystream_portion)
    
    # Output the result
    result = {
        "plaintext": bytes_to_hex(pt1_portion)
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
