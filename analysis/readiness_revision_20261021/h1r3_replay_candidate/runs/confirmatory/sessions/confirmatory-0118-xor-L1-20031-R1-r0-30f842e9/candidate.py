import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse the instance
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Build a mapping of (message_index, offset) -> ciphertext bytes
    cipher_map = {}
    for ct in ciphertexts:
        msg_idx = ct['message_index']
        data = bytes.fromhex(ct['data'])
        cipher_map[msg_idx] = data
    
    # Build a mapping of (message_index, offset) -> plaintext bytes
    plain_map = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        data = bytes.fromhex(kp['data'])
        plain_map[(msg_idx, offset)] = data
    
    # This is a two-time pad (stream cipher key reuse) attack
    # C0 = P0 XOR K
    # C1 = P1 XOR K
    # Given C0, C1, and P0, we can recover P1:
    # K = P0 XOR C0
    # P1 = C1 XOR K = C1 XOR (P0 XOR C0) = C1 XOR P0 XOR C0
    
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Find the known plaintext that helps us
    known_msg_idx = known_plaintexts[0]['message_index']
    known_offset = known_plaintexts[0]['offset']
    known_plain = bytes.fromhex(known_plaintexts[0]['data'])
    
    # Get the ciphertexts
    cipher_known = cipher_map[known_msg_idx]
    cipher_target = cipher_map[target_msg_idx]
    
    # Extract the keystream from the known plaintext/ciphertext pair
    # K = P0 XOR C0
    keystream = bytes(p ^ c for p, c in zip(known_plain, cipher_known[known_offset:known_offset + len(known_plain)]))
    
    # Decrypt the target using the keystream
    # P1 = C1 XOR K
    plaintext_bytes = bytes(c ^ k for c, k in zip(
        cipher_target[target_offset:target_offset + target_length],
        keystream[target_offset:target_offset + target_length]
    ))
    
    plaintext_hex = plaintext_bytes.hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
