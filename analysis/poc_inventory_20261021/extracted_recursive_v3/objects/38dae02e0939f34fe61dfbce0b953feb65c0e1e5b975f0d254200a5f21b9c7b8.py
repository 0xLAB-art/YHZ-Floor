import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert hex ciphertexts to bytes
    ct_bytes = []
    for ct in ciphertexts:
        ct_bytes.append(bytes.fromhex(ct['data']))
    
    # This is a many-time pad attack
    # XOR of two ciphertexts cancels the keystream: C1 ⊕ C2 = P1 ⊕ P2
    # With known plaintexts, we can recover keystream bytes
    
    # Build keystream for each message
    max_len = max(len(ct) for ct in ct_bytes)
    keystreams = [bytearray([None] * len(ct)) for ct in ct_bytes]
    
    # Extract keystream from known plaintexts
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext = bytes.fromhex(kp['data'])
        
        for i, p_byte in enumerate(plaintext):
            pos = offset + i
            if pos < len(ct_bytes[msg_idx]):
                # keystream[pos] = ciphertext[pos] ⊕ plaintext[pos]
                k_byte = ct_bytes[msg_idx][pos] ^ p_byte
                keystreams[msg_idx][pos] = k_byte
    
    # Propagate keystream knowledge across messages
    # If we know keystream at position i for message j, we can recover plaintext
    # at position i for all other messages, then use that to recover more keystream
    
    changed = True
    iterations = 0
    while changed and iterations < 100:
        changed = False
        iterations += 1
        
        for pos in range(max_len):
            # Collect known keystream bytes at this position
            known_k = []
            for msg_idx in range(len(ct_bytes)):
                if pos < len(keystreams[msg_idx]) and keystreams[msg_idx][pos] is not None:
                    known_k.append(keystreams[msg_idx][pos])
            
            if not known_k:
                continue
            
            # Use majority vote or first known value (assuming same key reuse)
            # In a stream cipher reuse attack, the keystream should be identical
            k_byte = known_k[0]
            
            # Propagate to all messages at this position
            for msg_idx in range(len(ct_bytes)):
                if pos < len(ct_bytes[msg_idx]):
                    if keystreams[msg_idx][pos] is None:
                        keystreams[msg_idx][pos] = k_byte
                        changed = True
    
    # Extract target plaintext
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    result = bytearray(target_length)
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(keystreams[target_msg_idx]) and keystreams[target_msg_idx][pos] is not None:
            result[i] = ct_bytes[target_msg_idx][pos] ^ keystreams[target_msg_idx][pos]
        else:
            # If we don't have the keystream, we can't decrypt
            # Try to infer from context or use a placeholder
            result[i] = 0
    
    print(json.dumps({"plaintext": result.hex()}))

if __name__ == "__main__":
    main()