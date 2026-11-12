import sys
import json

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse the data
    ciphertexts = {ct['message_index']: ct['data'] for ct in instance['ciphertexts']}
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Get the known plaintext (message 0, offset 0)
    known_pt = known_plaintexts[0]
    known_msg_idx = known_pt['message_index']
    known_offset = known_pt['offset']
    known_data = bytes.fromhex(known_pt['data'])
    
    # Get ciphertext for the known message
    ct_known = bytes.fromhex(ciphertexts[known_msg_idx])
    
    # Get target ciphertext
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    ct_target = bytes.fromhex(ciphertexts[target_msg_idx])
    
    # Extract the keystream from known plaintext
    # K = P1 ⊕ C1
    keystream_start = known_offset
    keystream_end = known_offset + len(known_data)
    keystream = bytes(p ^ c for p, c in zip(known_data, ct_known[keystream_start:keystream_end]))
    
    # Decrypt the target using the recovered keystream
    # P2 = C2 ⊕ K
    plaintext_bytes = bytes(c ^ k for c, k in zip(
        ct_target[target_offset:target_offset + target_length],
        keystream[target_offset:target_offset + target_length]
    ))
    
    # Output result
    result = {
        "plaintext": plaintext_bytes.hex()
    }
    print(json.dumps(result))

if __name__ == '__main__':
    main()