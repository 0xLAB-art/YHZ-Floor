import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Build a mapping from message_index to ciphertext bytes
    cipher_map = {}
    for ct in ciphertexts:
        cipher_map[ct['message_index']] = bytes.fromhex(ct['data'])
    
    # Initialize known plaintext bytes for all messages
    plaintext_map = {}
    for msg_idx in cipher_map:
        plaintext_map[msg_idx] = {}
    
    # Fill in known plaintexts
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        data_bytes = bytes.fromhex(kp['data'])
        for i, b in enumerate(data_bytes):
            plaintext_map[msg_idx][offset + i] = b
    
    # Recover keystream from known plaintexts
    keystream = {}
    for msg_idx in plaintext_map:
        for pos, plain_byte in plaintext_map[msg_idx].items():
            cipher_byte = cipher_map[msg_idx][pos]
            key_byte = cipher_byte ^ plain_byte
            if pos in keystream and keystream[pos] != key_byte:
                # Inconsistency check (shouldn't happen with valid data)
                pass
            keystream[pos] = key_byte
    
    # Decrypt target message using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_cipher = cipher_map[target_msg_idx]
    target_plaintext = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            # We know the keystream at this position
            plain_byte = target_cipher[pos] ^ keystream[pos]
            target_plaintext.append(plain_byte)
        else:
            # We don't have keystream for this position
            # Try to use crib-dragging or frequency analysis
            # For now, we'll try common patterns
            # This is a fallback - in practice we need more sophisticated attack
            target_plaintext.append(0)
    
    # Try to recover more keystream using crib-dragging
    # Common English patterns and words
    common_bytes = [0x20, 0x65, 0x74, 0x61, 0x6f, 0x69, 0x6e, 0x73, 0x68, 0x72]  # space, e, t, a, o, i, n, s, h, r
    
    # Iteratively try to recover more keystream
    max_iterations = 100
    for iteration in range(max_iterations):
        improved = False
        
        for pos in range(256):  # Check all possible positions
            if pos in keystream:
                continue
            
            # Try XORing all ciphertexts at this position
            xor_results = []
            for msg_idx in cipher_map:
                if pos < len(cipher_map[msg_idx]):
                    xor_results.append((msg_idx, cipher_map[msg_idx][pos]))
            
            if len(xor_results) < 2:
                continue
            
            # Try to deduce keystream from XOR relationships
            for i in range(len(xor_results)):
                msg_idx_i, cipher_i = xor_results[i]
                if pos in plaintext_map[msg_idx_i]:
                    # We know this plaintext, compute keystream
                    plain_i = plaintext_map[msg_idx_i][pos]
                    key_byte = cipher_i ^ plain_i
                    keystream[pos] = key_byte
                    improved = True
                    
                    # Now decrypt all other messages at this position
                    for j in range(len(xor_results)):
                        msg_idx_j, cipher_j = xor_results[j]
                        if msg_idx_j != msg_idx_i:
                            plain_j = cipher_j ^ key_byte
                            plaintext_map[msg_idx_j][pos] = plain_j
                    break
        
        if not improved:
            break
    
    # Final decryption of target
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            plain_byte = target_cipher[pos] ^ keystream[pos]
            target_plaintext[i] = plain_byte
    
    result = bytes(target_plaintext).hex()
    print(json.dumps({"plaintext": result}))

if __name__ == "__main__":
    main()