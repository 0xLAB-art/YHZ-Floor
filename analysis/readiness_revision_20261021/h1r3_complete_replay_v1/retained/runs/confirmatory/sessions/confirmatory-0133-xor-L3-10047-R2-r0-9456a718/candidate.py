import sys
import json
import base64
from typing import List, Tuple, Dict

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse input
    ciphertexts = []
    for ct in instance['ciphertexts']:
        data = base64.b64decode(ct['data'])
        ciphertexts.append((ct['message_index'], data))
    
    known_plaintexts = []
    for kp in instance['known_plaintexts']:
        data = base64.b64decode(kp['data'])
        known_plaintexts.append((kp['message_index'], kp['offset'], data))
    
    target_msg_idx = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    # Build ciphertext array indexed by message_index
    max_idx = max(idx for idx, _ in ciphertexts)
    ct_array = [None] * (max_idx + 1)
    for idx, data in ciphertexts:
        ct_array[idx] = data
    
    # This is a many-time pad attack
    # XOR property: if C1 = P1 ⊕ K and C2 = P2 ⊕ K (same key K)
    # then C1 ⊕ C2 = P1 ⊕ P2
    # If we know P1, we can find K = C1 ⊕ P1
    # Then we can decrypt any other ciphertext: P = C ⊕ K
    
    # Find the maximum ciphertext length to know keystream length
    max_len = max(len(data) for _, data in ciphertexts)
    
    # Recover keystream
    keystream = [None] * max_len
    
    # Use known plaintexts to recover keystream bytes
    for msg_idx, offset, plaintext in known_plaintexts:
        ciphertext = ct_array[msg_idx]
        for i, p_byte in enumerate(plaintext):
            pos = offset + i
            if pos < len(ciphertext):
                # K[pos] = C[pos] ⊕ P[pos]
                k_byte = ciphertext[pos] ^ p_byte
                if keystream[pos] is None:
                    keystream[pos] = k_byte
                elif keystream[pos] != k_byte:
                    # Consistency check - should not happen with correct data
                    pass
    
    # Now decrypt the target
    target_ciphertext = ct_array[target_msg_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(target_ciphertext) and keystream[pos] is not None:
            p_byte = target_ciphertext[pos] ^ keystream[pos]
            plaintext_bytes.append(p_byte)
        else:
            # If we don't have the keystream byte, we need to try to recover it
            # or make an educated guess. For now, this shouldn't happen if the
            # known plaintexts give us full coverage
            plaintext_bytes.append(0)
    
    # Convert to hex
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    # Output
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
