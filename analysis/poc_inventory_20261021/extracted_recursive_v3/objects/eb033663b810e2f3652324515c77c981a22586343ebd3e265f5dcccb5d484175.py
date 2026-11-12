import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse the instance
    ciphertexts = {ct['message_index']: bytes.fromhex(ct['data']) for ct in instance['ciphertexts']}
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Get the known plaintext and corresponding ciphertext
    known_pt = known_plaintexts[0]
    known_plaintext = bytes.fromhex(known_pt['data'])
    known_msg_idx = known_pt['message_index']
    known_offset = known_pt['offset']
    known_ciphertext = ciphertexts[known_msg_idx]
    
    # Extract the keystream from the known plaintext/ciphertext pair
    # In a stream cipher: ciphertext = plaintext XOR keystream
    # Therefore: keystream = plaintext XOR ciphertext
    keystream_start = known_offset
    keystream_end = known_offset + len(known_plaintext)
    keystream = bytes(p ^ c for p, c in zip(known_plaintext, known_ciphertext[keystream_start:keystream_end]))
    
    # Get target ciphertext
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    target_ciphertext = ciphertexts[target_msg_idx]
    
    # Decrypt the target using the recovered keystream
    # plaintext = ciphertext XOR keystream
    target_ct_segment = target_ciphertext[target_offset:target_offset + target_length]
    plaintext = bytes(c ^ k for c, k in zip(target_ct_segment, keystream[:target_length]))
    
    result = {
        "plaintext": plaintext.hex()
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()