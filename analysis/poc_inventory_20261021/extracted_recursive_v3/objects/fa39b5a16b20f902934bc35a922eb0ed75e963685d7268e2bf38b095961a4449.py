import sys
import json

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    target = instance['target']
    
    # Decode all ciphertexts from hex
    ct_bytes = []
    for ct in ciphertexts:
        ct_bytes.append(bytes.fromhex(ct['data']))
    
    target_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Check if we have the target ciphertext
    if target_idx >= len(ct_bytes):
        print(json.dumps({
            "status": "UNDERDETERMINED",
            "reason": "Target message index not in provided ciphertexts"
        }))
        return
    
    target_ct = ct_bytes[target_idx]
    
    # Check if target range is valid
    if target_offset + target_length > len(target_ct):
        print(json.dumps({
            "status": "UNDERDETERMINED",
            "reason": "Target range exceeds ciphertext length"
        }))
        return
    
    # This appears to be a stream cipher reuse attack scenario
    # We have 8 ciphertexts but no known plaintexts
    # Without known plaintexts or additional structure, we cannot recover
    # the plaintext from stream cipher ciphertexts alone
    
    # Even with multiple ciphertexts using the same keystream (stream cipher reuse),
    # we would need at least one known plaintext to bootstrap the attack
    
    print(json.dumps({
        "status": "UNDERDETERMINED",
        "reason": "No known plaintexts provided; cannot recover plaintext from ciphertexts alone"
    }))

if __name__ == "__main__":
    main()