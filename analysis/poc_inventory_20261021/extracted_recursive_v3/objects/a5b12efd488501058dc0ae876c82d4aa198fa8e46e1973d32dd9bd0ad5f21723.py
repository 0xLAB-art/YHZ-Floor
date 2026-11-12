import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    # Parse the instance
    ciphertexts = {ct['message_index']: bytes.fromhex(ct['data']) for ct in instance['ciphertexts']}
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Get the known plaintext for message 0
    known_pt = None
    for kp in known_plaintexts:
        if kp['message_index'] == 0:
            known_pt = bytes.fromhex(kp['data'])
            known_offset = kp['offset']
            break
    
    # Get ciphertexts
    ct0 = ciphertexts[0]
    ct1 = ciphertexts[1]
    
    # This is a stream cipher reuse attack (two-time pad)
    # ct0 = pt0 XOR key
    # ct1 = pt1 XOR key
    # We know pt0, so we can recover the key at those positions
    # key = pt0 XOR ct0
    
    # Extract the key from the known plaintext region
    key_start = known_offset
    key_end = known_offset + len(known_pt)
    key_fragment = bytes(known_pt[i] ^ ct0[key_start + i] for i in range(len(known_pt)))
    
    # Now decrypt target message using the recovered key
    target_msg_index = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ct = ciphertexts[target_msg_index]
    
    # Decrypt the target region
    plaintext_bytes = bytes(target_ct[target_offset + i] ^ key_fragment[i] for i in range(target_length))
    plaintext_hex = plaintext_bytes.hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()