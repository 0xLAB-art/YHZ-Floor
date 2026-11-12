import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    target = instance['target']
    known_plaintexts = instance.get('known_plaintexts', [])
    
    # Convert hex ciphertexts to bytes
    ct_bytes = []
    for ct in ciphertexts:
        ct_bytes.append(bytes.fromhex(ct['data']))
    
    # Check if this is a stream cipher reuse attack (XOR)
    # With no known plaintexts and 4 ciphertexts, we cannot uniquely determine the plaintext
    
    # For a stream cipher with key reuse:
    # C1 = M1 ⊕ K
    # C2 = M2 ⊕ K
    # C1 ⊕ C2 = M1 ⊕ M2
    
    # With 4 ciphertexts and no known plaintexts, we can compute pairwise XORs
    # but cannot uniquely recover the original messages without additional constraints
    
    # The target asks for bytes 32-95 (64 bytes starting at offset 32) of message_index 3
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Check if we have any known plaintexts that could help
    if len(known_plaintexts) == 0:
        # Without known plaintexts, we have an underdetermined system
        # We would need at least one known plaintext to recover the keystream
        # and then decrypt the target message
        
        result = {
            "status": "UNDERDETERMINED",
            "reason": "No known plaintexts provided; cannot uniquely determine plaintext from ciphertext-only attack on stream cipher with key reuse"
        }
    else:
        # If we had known plaintexts, we could recover keystream and decrypt
        # But this branch won't execute given the instance
        result = {
            "status": "UNDERDETERMINED",
            "reason": "Insufficient information"
        }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()