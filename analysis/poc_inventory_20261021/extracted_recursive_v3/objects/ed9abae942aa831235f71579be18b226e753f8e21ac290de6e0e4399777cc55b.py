import sys
import json

def hex_to_bytes(h):
    return bytes.fromhex(h)

def bytes_to_hex(b):
    return b.hex()

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = {ct['message_index']: hex_to_bytes(ct['data']) 
                   for ct in instance['ciphertexts']}
    known = instance['known_plaintexts']
    
    # Find max length needed
    max_len = max(len(ct) for ct in ciphertexts.values())
    
    # Recover keystream from known plaintexts
    keystream = [None] * max_len
    
    for kp in known:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = hex_to_bytes(kp['data'])
        ciphertext = ciphertexts[msg_idx]
        
        for i, pb in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ciphertext):
                keystream[pos] = ciphertext[pos] ^ pb
    
    # Recover all plaintexts where we have keystream
    plaintexts = {}
    for msg_idx, ct in ciphertexts.items():
        pt = []
        for i in range(len(ct)):
            if keystream[i] is not None:
                pt.append(ct[i] ^ keystream[i])
            else:
                pt.append(None)
        plaintexts[msg_idx] = pt
    
    # Use crib-dragging: XOR pairs of ciphertexts to find space-letter patterns
    # When two messages are XORed, space XOR letter = letter ^ 0x20
    # This gives us characteristic patterns
    
    def likely_space_xor_letter(b):
        # space (0x20) XOR letter gives recognizable patterns
        # Check if XORing with space gives a letter
        candidate = b ^ 0x20
        return (ord('A') <= candidate <= ord('Z')) or (ord('a') <= candidate <= ord('z'))
    
    # Iteratively improve keystream using XOR analysis
    for _ in range(10):  # Multiple passes
        for i in range(max_len):
            if keystream[i] is not None:
                continue
            
            # Try to deduce keystream[i] from XOR patterns
            candidates = []
            
            for msg_idx in ciphertexts:
                if i >= len(ciphertexts[msg_idx]):
                    continue
                    
                # Look at other messages at same position
                for other_idx in ciphertexts:
                    if other_idx == msg_idx or i >= len(ciphertexts[other_idx]):
                        continue
                    
                    # If we know plaintext of other message at position i
                    if plaintexts[other_idx][i] is not None:
                        # We can recover this message's plaintext
                        xor_val = ciphertexts[msg_idx][i] ^ ciphertexts[other_idx][i]
                        pt_char = xor_val ^ plaintexts[other_idx][i]
                        
                        # Deduce keystream
                        ks = ciphertexts[msg_idx][i] ^ pt_char
                        candidates.append(ks)
            
            if candidates:
                # Use most common candidate
                keystream[i] = max(set(candidates), key=candidates.count)
    
    # Extract target plaintext
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    result = []
    ct = ciphertexts[target_msg_idx]
    
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(ct) and keystream[pos] is not None:
            result.append(ct[pos] ^ keystream[pos])
        else:
            result.append(0)  # Fallback
    
    plaintext_hex = bytes_to_hex(bytes(result))
    print(json.dumps({"plaintext": plaintext_hex}))

if __name__ == '__main__':
    main()