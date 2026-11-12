import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert hex ciphertexts to bytes
    ct_bytes = []
    for ct in ciphertexts:
        ct_bytes.append(bytes.fromhex(ct['data']))
    
    # This is a many-time pad attack (stream cipher key reuse)
    # XOR property: C1 XOR C2 = P1 XOR P2
    # If we know P1, we can recover the keystream: K = C1 XOR P1
    # Then use K to decrypt other messages: P = C XOR K
    
    # Build keystream from known plaintexts
    max_len = max(len(ct) for ct in ct_bytes)
    keystream = [None] * max_len
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = bytes.fromhex(kp['data'])
        
        # Extract keystream: keystream = ciphertext XOR plaintext
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ct_bytes[msg_idx]):
                key_byte = ct_bytes[msg_idx][pos] ^ pt_byte
                keystream[pos] = key_byte
    
    # Now decrypt the target using the recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    result = []
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(keystream) and keystream[pos] is not None:
            # Decrypt: plaintext = ciphertext XOR keystream
            plaintext_byte = ct_bytes[target_msg_idx][pos] ^ keystream[pos]
            result.append(plaintext_byte)
        else:
            # If keystream is unknown at this position, we can't decrypt
            # This shouldn't happen if the challenge is solvable
            result.append(0)
    
    plaintext_hex = bytes(result).hex()
    
    output = {"plaintext": plaintext_hex}
    print(json.dumps(output))

if __name__ == '__main__':
    main()