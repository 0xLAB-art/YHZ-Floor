import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    # Parse the instance
    ciphertexts = {ct['message_index']: bytes.fromhex(ct['data']) for ct in instance['ciphertexts']}
    known_plaintexts = {kp['message_index']: (kp['offset'], bytes.fromhex(kp['data'])) for kp in instance['known_plaintexts']}
    target = instance['target']
    
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Find a known plaintext to use for keystream recovery
    known_msg_idx = list(known_plaintexts.keys())[0]
    known_offset, known_plaintext = known_plaintexts[known_msg_idx]
    known_ciphertext = ciphertexts[known_msg_idx]
    
    # Recover keystream from known plaintext/ciphertext pair
    keystream = bytes(p ^ c for p, c in zip(known_plaintext, known_ciphertext[known_offset:known_offset + len(known_plaintext)]))
    
    # Use the recovered keystream to decrypt the target
    target_ciphertext = ciphertexts[target_msg_idx]
    plaintext = bytes(keystream[i] ^ target_ciphertext[target_offset + i] for i in range(target_length))
    
    result = {
        "plaintext": plaintext.hex()
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()