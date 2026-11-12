import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse the instance
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Find the ciphertext and known plaintext for message 0
    ct0 = None
    pt0 = None
    
    for ct in ciphertexts:
        if ct['message_index'] == 0:
            ct0 = bytes.fromhex(ct['data'])
            break
    
    for kp in known_plaintexts:
        if kp['message_index'] == 0:
            pt0 = bytes.fromhex(kp['data'])
            break
    
    # Find the ciphertext for the target message
    ct_target = None
    for ct in ciphertexts:
        if ct['message_index'] == target['message_index']:
            ct_target = bytes.fromhex(ct['data'])
            break
    
    # XOR attack: if both messages use the same key stream (stream cipher reuse)
    # ct0 = pt0 XOR key
    # ct1 = pt1 XOR key
    # Therefore: key = ct0 XOR pt0
    # And: pt1 = ct1 XOR key = ct1 XOR ct0 XOR pt0
    
    # Extract the key stream from message 0
    key_stream = bytes(c ^ p for c, p in zip(ct0, pt0))
    
    # Decrypt the target message
    offset = target['offset']
    length = target['length']
    
    plaintext = bytes(ct_target[i] ^ key_stream[i] for i in range(offset, offset + length))
    
    result = {
        "plaintext": plaintext.hex()
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()