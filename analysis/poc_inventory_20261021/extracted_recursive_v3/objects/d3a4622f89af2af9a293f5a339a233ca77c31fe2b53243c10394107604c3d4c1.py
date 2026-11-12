import json
import sys

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Find the ciphertext for message_index 0 and 1
    ct0 = None
    ct1 = None
    for ct in ciphertexts:
        if ct['message_index'] == 0:
            ct0 = bytes.fromhex(ct['data'])
        elif ct['message_index'] == 1:
            ct1 = bytes.fromhex(ct['data'])
    
    # Find the known plaintext for message_index 0
    pt0 = None
    for kp in known_plaintexts:
        if kp['message_index'] == 0:
            pt0 = bytes.fromhex(kp['data'])
            pt0_offset = kp['offset']
    
    # This is a stream cipher reuse attack
    # ct0 = pt0 XOR keystream
    # ct1 = pt1 XOR keystream
    # We know pt0 and ct0, so we can recover the keystream
    # keystream = pt0 XOR ct0
    # Then pt1 = ct1 XOR keystream
    
    # Extract the relevant portion of the keystream
    keystream_offset = pt0_offset
    keystream_length = len(pt0)
    keystream = bytes(p ^ c for p, c in zip(pt0, ct0[keystream_offset:keystream_offset + keystream_length]))
    
    # Now recover the plaintext for message_index 1
    target_offset = target['offset']
    target_length = target['length']
    
    # We need the keystream from target_offset to target_offset + target_length
    # We have keystream from keystream_offset to keystream_offset + keystream_length
    # Check if we have enough keystream
    keystream_start = keystream_offset
    keystream_end = keystream_offset + keystream_length
    
    pt1_bytes = bytes(c ^ keystream[i - keystream_start] 
                      for i, c in enumerate(ct1[target_offset:target_offset + target_length], 
                                           start=target_offset))
    
    result = {
        "plaintext": pt1_bytes.hex()
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
