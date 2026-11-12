import sys
import json
import base64

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode ciphertexts
    ciphertexts = {}
    for ct in instance['ciphertexts']:
        idx = ct['message_index']
        ciphertexts[idx] = base64.b64decode(ct['data'])
    
    # Decode known plaintexts
    known = {}
    for kp in instance['known_plaintexts']:
        idx = kp['message_index']
        offset = kp['offset']
        data = base64.b64decode(kp['data'])
        if idx not in known:
            known[idx] = {}
        for i, byte in enumerate(data):
            known[idx][offset + i] = byte
    
    # Extract target info
    target_msg = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    # Recover keystream from known plaintexts
    keystream = {}
    for msg_idx, positions in known.items():
        for pos, plaintext_byte in positions.items():
            ciphertext_byte = ciphertexts[msg_idx][pos]
            keystream[pos] = plaintext_byte ^ ciphertext_byte
    
    # Decrypt target using recovered keystream
    result = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            # We have the keystream at this position
            plaintext_byte = ciphertexts[target_msg][pos] ^ keystream[pos]
            result.append(plaintext_byte)
        else:
            # Try to recover keystream from other messages
            # If we have plaintext for any other message at this position
            recovered = False
            for msg_idx in known:
                if pos in known[msg_idx]:
                    # Recover keystream from this known plaintext
                    k = known[msg_idx][pos] ^ ciphertexts[msg_idx][pos]
                    plaintext_byte = ciphertexts[target_msg][pos] ^ k
                    result.append(plaintext_byte)
                    recovered = True
                    break
            
            if not recovered:
                # Cannot recover - should not happen with proper instance
                result.append(0)
    
    # Convert to hex
    plaintext_hex = bytes(result).hex()
    
    # Output
    output = {"plaintext": plaintext_hex}
    print(json.dumps(output))

if __name__ == "__main__":
    main()