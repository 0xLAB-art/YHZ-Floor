import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse ciphertexts
    ciphertexts = {}
    for ct in instance['ciphertexts']:
        msg_idx = ct['message_index']
        data = bytes.fromhex(ct['data'])
        ciphertexts[msg_idx] = data
    
    # Parse known plaintexts
    known_plaintexts = {}
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        offset = kp['offset']
        data = bytes.fromhex(kp['data'])
        if msg_idx not in known_plaintexts:
            known_plaintexts[msg_idx] = {}
        known_plaintexts[msg_idx][offset] = data
    
    # Parse target
    target_msg_idx = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    # Stream cipher attack: C1 XOR C2 = P1 XOR P2
    # If we know P1, we can recover P2
    
    # Find known plaintext for a different message
    known_msg_idx = None
    known_offset = None
    known_data = None
    
    for msg_idx in known_plaintexts:
        if msg_idx != target_msg_idx:
            for offset, data in known_plaintexts[msg_idx].items():
                known_msg_idx = msg_idx
                known_offset = offset
                known_data = data
                break
            if known_msg_idx is not None:
                break
    
    if known_msg_idx is None:
        # No known plaintext for another message
        result = {"plaintext": "00" * target_length}
    else:
        # Extract the keystream from the known message
        # Keystream = Ciphertext XOR Plaintext
        known_ct = ciphertexts[known_msg_idx]
        keystream_start = known_offset
        keystream_end = known_offset + len(known_data)
        
        keystream = bytes(known_ct[i] ^ known_data[i - known_offset] 
                         for i in range(keystream_start, keystream_end))
        
        # Use the keystream to decrypt the target message
        target_ct = ciphertexts[target_msg_idx]
        
        # Calculate overlap between keystream and target
        overlap_start = max(target_offset, keystream_start)
        overlap_end = min(target_offset + target_length, keystream_end)
        
        if overlap_start < overlap_end:
            # We have overlap
            plaintext = bytearray(target_length)
            
            for i in range(target_offset, target_offset + target_length):
                if keystream_start <= i < keystream_end:
                    # We know the keystream at this position
                    ks_byte = keystream[i - keystream_start]
                    plaintext[i - target_offset] = target_ct[i] ^ ks_byte
                else:
                    # No keystream known
                    plaintext[i - target_offset] = 0
            
            result = {"plaintext": plaintext.hex()}
        else:
            # No overlap
            result = {"plaintext": "00" * target_length}
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()