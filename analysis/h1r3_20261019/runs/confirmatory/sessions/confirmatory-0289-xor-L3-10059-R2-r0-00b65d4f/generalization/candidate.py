import sys
import json
import base64

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode all ciphertexts
    ciphertexts = []
    for ct in instance['ciphertexts']:
        ciphertexts.append(base64.b64decode(ct['data']))
    
    # Decode known plaintexts
    known = {}
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = base64.b64decode(kp['data'])
        
        if msg_idx not in known:
            known[msg_idx] = {}
        
        for i, byte in enumerate(plaintext_bytes):
            known[msg_idx][offset + i] = byte
    
    # Extract keystream using known plaintexts
    # keystream[position] = ciphertext[position] XOR plaintext[position]
    keystream = {}
    
    for msg_idx in known:
        for pos in known[msg_idx]:
            plaintext_byte = known[msg_idx][pos]
            ciphertext_byte = ciphertexts[msg_idx][pos]
            keystream_byte = ciphertext_byte ^ plaintext_byte
            
            # Store keystream (should be consistent across messages if same key reused)
            if pos in keystream:
                # Verify consistency
                if keystream[pos] != keystream_byte:
                    pass  # In case of stream cipher with different keys
            keystream[pos] = keystream_byte
    
    # Decrypt target message using recovered keystream
    target_msg_idx = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    plaintext = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            # Decrypt using known keystream
            ciphertext_byte = ciphertexts[target_msg_idx][pos]
            plaintext_byte = ciphertext_byte ^ keystream[pos]
            plaintext.append(plaintext_byte)
        else:
            # Try to recover keystream from other messages through crib-dragging
            # or XOR relationships between ciphertexts
            # For now, we'll use statistical analysis
            
            # XOR all ciphertexts at this position to find patterns
            # This is a many-time pad attack
            candidates = []
            for other_idx in range(len(ciphertexts)):
                if other_idx == target_msg_idx:
                    continue
                if pos < len(ciphertexts[other_idx]):
                    # Try common characters and see if XOR produces readable text
                    ct_xor = ciphertexts[target_msg_idx][pos] ^ ciphertexts[other_idx][pos]
                    
                    # Check if we know plaintext for the other message
                    if other_idx in known and pos in known[other_idx]:
                        other_plain = known[other_idx][pos]
                        # target_plain ^ other_plain = ct_xor
                        target_plain = ct_xor ^ other_plain
                        candidates.append(target_plain)
            
            if candidates:
                # Use most common candidate
                plaintext_byte = max(set(candidates), key=candidates.count)
                plaintext.append(plaintext_byte)
            else:
                # Guess space (0x20) as most common character
                plaintext.append(0x20)
    
    # Convert to hex
    plaintext_hex = ''.join(f'{b:02x}' for b in plaintext)
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
