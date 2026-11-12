import sys
import json
import base64

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse the input
    ciphertexts = {ct['message_index']: base64.b64decode(ct['data']) 
                   for ct in instance['ciphertexts']}
    
    known_plaintexts = {}
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext = base64.b64decode(kp['data'])
        if msg_idx not in known_plaintexts:
            known_plaintexts[msg_idx] = {}
        known_plaintexts[msg_idx][offset] = plaintext
    
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Two-time pad attack: if the same keystream is reused for multiple messages,
    # we can XOR ciphertexts together and use known plaintext to recover the other
    
    # Get the ciphertext blocks
    ct0 = ciphertexts[0]
    ct1 = ciphertexts[1]
    
    # Get the known plaintext for message 0
    pt0 = known_plaintexts[0][0]
    
    # Recover the keystream for message 0
    # ct0 = pt0 XOR keystream
    # keystream = pt0 XOR ct0
    keystream = bytes(p ^ c for p, c in zip(pt0, ct0))
    
    # Use the same keystream to decrypt message 1
    # ct1 = pt1 XOR keystream
    # pt1 = ct1 XOR keystream
    pt1_start = target_offset
    pt1_end = target_offset + target_length
    
    plaintext = bytes(c ^ k for c, k in zip(ct1[pt1_start:pt1_end], 
                                             keystream[pt1_start:pt1_end]))
    
    result = {
        "plaintext": plaintext.hex()
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
