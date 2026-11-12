import sys
import json
import base64

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse ciphertexts
    ciphertexts = {}
    for ct in instance['ciphertexts']:
        idx = ct['message_index']
        data = base64.b64decode(ct['data'])
        ciphertexts[idx] = data
    
    # Parse known plaintexts
    known = {}
    for kp in instance['known_plaintexts']:
        idx = kp['message_index']
        offset = kp['offset']
        plaintext = base64.b64decode(kp['data'])
        if idx not in known:
            known[idx] = {}
        for i, byte in enumerate(plaintext):
            known[idx][offset + i] = byte
    
    # Target
    target_idx = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    # Extract keystream bytes from known plaintexts
    keystream = {}
    for idx, positions in known.items():
        for pos, plain_byte in positions.items():
            cipher_byte = ciphertexts[idx][pos]
            key_byte = cipher_byte ^ plain_byte
            if pos not in keystream:
                keystream[pos] = key_byte
            elif keystream[pos] != key_byte:
                # Inconsistency - shouldn't happen with stream cipher reuse
                pass
    
    # Decrypt target using recovered keystream
    result = []
    target_ct = ciphertexts[target_idx]
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            plain_byte = target_ct[pos] ^ keystream[pos]
            result.append(plain_byte)
        else:
            # No keystream byte available - this shouldn't happen if puzzle is solvable
            # Try to infer from ciphertext XOR patterns
            result.append(0)
    
    # Convert to hex
    plaintext_hex = bytes(result).hex()
    
    print(json.dumps({"plaintext": plaintext_hex}))

if __name__ == "__main__":
    main()