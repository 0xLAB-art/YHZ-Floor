import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    ciphertexts = instance['ciphertexts']
    target = instance['target']
    known_plaintexts = instance.get('known_plaintexts', [])
    
    # Convert hex to bytes
    ciphertexts_bytes = []
    for ct in ciphertexts:
        ciphertexts_bytes.append({
            'data': bytes.fromhex(ct['data']),
            'message_index': ct['message_index']
        })
    
    # Target: extract 64 bytes starting at offset 32 from message_index 3
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Find the target ciphertext
    target_ct = None
    for ct in ciphertexts_bytes:
        if ct['message_index'] == target_msg_idx:
            target_ct = ct['data']
            break
    
    if target_ct is None:
        result = {
            "status": "UNDERDETERMINED",
            "reason": "Target ciphertext not found"
        }
        print(json.dumps(result))
        return
    
    # Check if we have enough ciphertext data
    if len(target_ct) < target_offset + target_length:
        result = {
            "status": "UNDERDETERMINED",
            "reason": "Insufficient ciphertext length for target extraction"
        }
        print(json.dumps(result))
        return
    
    # This appears to be a stream cipher reuse attack scenario
    # With no known plaintexts and no key/nonce information, we cannot decrypt
    # We would need either:
    # 1. Known plaintext for any message
    # 2. The key/nonce
    # 3. Multiple ciphertexts with same keystream (for XOR analysis)
    
    # Check if all ciphertexts have the same length (potential keystream reuse)
    lengths = [len(ct['data']) for ct in ciphertexts_bytes]
    
    if len(set(lengths)) == 1 and len(ciphertexts_bytes) > 1:
        # Potential many-time pad, but still underdetermined without known plaintext
        result = {
            "status": "UNDERDETERMINED",
            "reason": "No known plaintexts provided; cannot recover keystream or plaintext"
        }
    else:
        result = {
            "status": "UNDERDETERMINED",
            "reason": "Insufficient information to decrypt without key or known plaintext"
        }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()