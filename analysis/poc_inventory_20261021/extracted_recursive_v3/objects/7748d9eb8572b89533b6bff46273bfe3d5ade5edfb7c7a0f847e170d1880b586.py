import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    # Parse the instance
    ciphertexts = {ct['message_index']: bytes.fromhex(ct['data']) for ct in instance['ciphertexts']}
    known_plaintexts = {kp['message_index']: {'data': bytes.fromhex(kp['data']), 'offset': kp['offset']} for kp in instance['known_plaintexts']}
    target = instance['target']
    
    # This is a stream cipher reuse attack (two-time pad)
    # If the same keystream is used for multiple messages:
    # C1 = P1 XOR K
    # C2 = P2 XOR K
    # Therefore: C1 XOR C2 = P1 XOR P2
    # If we know P1, we can recover P2: P2 = P1 XOR C1 XOR C2
    
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Find a known plaintext we can use
    known_msg_idx = list(known_plaintexts.keys())[0]
    known_plaintext = known_plaintexts[known_msg_idx]['data']
    known_offset = known_plaintexts[known_msg_idx]['offset']
    
    # Get ciphertexts
    known_ciphertext = ciphertexts[known_msg_idx]
    target_ciphertext = ciphertexts[target_msg_idx]
    
    # Recover the keystream from the known plaintext
    # K = P XOR C (for the known message)
    keystream = bytes([known_plaintext[i] ^ known_ciphertext[known_offset + i] for i in range(len(known_plaintext))])
    
    # Use the keystream to decrypt the target
    # P_target = C_target XOR K
    target_plaintext = bytes([target_ciphertext[target_offset + i] ^ keystream[i] for i in range(target_length)])
    
    result = {
        "plaintext": target_plaintext.hex()
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()