import sys
import json

def main():
    # Read instance
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
    # When the same key is reused, we can XOR ciphertexts together
    # C1 XOR C2 = (P1 XOR K) XOR (P2 XOR K) = P1 XOR P2
    
    # Build known plaintext bytes for each message
    messages = [bytearray(len(ct_bytes[i])) for i in range(len(ct_bytes))]
    known = [set() for _ in range(len(ct_bytes))]
    
    # Mark known plaintext positions
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        data = bytes.fromhex(kp['data'])
        for i, b in enumerate(data):
            if offset + i < len(messages[msg_idx]):
                messages[msg_idx][offset + i] = b
                known[msg_idx].add(offset + i)
    
    # Recover the keystream at positions where we have known plaintext
    # keystream[pos] = ciphertext[pos] XOR plaintext[pos]
    max_len = max(len(ct) for ct in ct_bytes)
    keystream = bytearray(max_len)
    keystream_known = set()
    
    for msg_idx in range(len(ct_bytes)):
        for pos in known[msg_idx]:
            key_byte = ct_bytes[msg_idx][pos] ^ messages[msg_idx][pos]
            keystream[pos] = key_byte
            keystream_known.add(pos)
    
    # Now we can decrypt the target message at positions where we know the keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    result = bytearray(target_length)
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream_known and pos < len(ct_bytes[target_msg_idx]):
            # Decrypt: plaintext = ciphertext XOR keystream
            result[i] = ct_bytes[target_msg_idx][pos] ^ keystream[pos]
        else:
            # Try to infer from other messages using crib-dragging or statistical analysis
            # For positions we don't know, we need to use the XOR relationships
            # between ciphertexts to infer likely plaintexts
            
            # Find a message where we know this position
            found = False
            for other_idx in range(len(ct_bytes)):
                if other_idx != target_msg_idx and pos in known[other_idx]:
                    if pos < len(ct_bytes[other_idx]) and pos < len(ct_bytes[target_msg_idx]):
                        # P_target[pos] = C_target[pos] XOR C_other[pos] XOR P_other[pos]
                        xor_val = ct_bytes[target_msg_idx][pos] ^ ct_bytes[other_idx][pos]
                        result[i] = xor_val ^ messages[other_idx][pos]
                        found = True
                        break
            
            if not found:
                # Last resort: use the keystream we recovered
                if pos < len(keystream) and pos in keystream_known:
                    result[i] = ct_bytes[target_msg_idx][pos] ^ keystream[pos]
    
    # Output result
    output = {"plaintext": result.hex()}
    print(json.dumps(output))

if __name__ == '__main__':
    main()
