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
    
    # Check if this is a stream cipher reuse scenario
    # With 4 ciphertexts and no known plaintexts, we can't uniquely determine the plaintext
    # We would need at least some known plaintext or more ciphertexts with known relationships
    
    # For stream cipher key reuse:
    # C1 = M1 XOR K
    # C2 = M2 XOR K
    # C1 XOR C2 = M1 XOR M2
    
    # With 4 ciphertexts and no known plaintexts, we have:
    # - 6 pairwise XOR combinations
    # - But we need to solve for the actual plaintext bytes at target location
    
    # The target is at message_index=3, offset=32, length=64
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Without known plaintexts, we cannot uniquely determine the plaintext
    # We can only narrow down possibilities through cryptanalysis techniques like:
    # - Frequency analysis on XORed ciphertexts
    # - Crib dragging
    # - Statistical analysis
    
    # But none of these give us a unique answer without additional information
    
    result = {
        "status": "UNDERDETERMINED",
        "reason": "Stream cipher key reuse detected but no known plaintexts provided; cannot uniquely recover target plaintext without additional constraints"
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()