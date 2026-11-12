import sys
import json
import base64
from collections import defaultdict

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode ciphertexts
    ciphertexts = []
    for ct in instance['ciphertexts']:
        data = base64.b64decode(ct['data'])
        ciphertexts.append({
            'data': data,
            'message_index': ct['message_index']
        })
    
    # Decode known plaintexts
    known_plaintexts = []
    for kp in instance['known_plaintexts']:
        data = base64.b64decode(kp['data'])
        known_plaintexts.append({
            'data': data,
            'message_index': kp['message_index'],
            'offset': kp['offset']
        })
    
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Build a mapping: message_index -> ciphertext bytes
    ct_map = {}
    for ct in ciphertexts:
        ct_map[ct['message_index']] = ct['data']
    
    # Build known keystream: position -> keystream byte
    # For stream cipher: C = P XOR K, so K = P XOR C
    keystream = defaultdict(lambda: None)
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = kp['data']
        ciphertext = ct_map[msg_idx]
        
        for i, p_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ciphertext):
                c_byte = ciphertext[pos]
                k_byte = p_byte ^ c_byte
                keystream[pos] = k_byte
    
    # Decrypt target using recovered keystream
    target_ct = ct_map[target_msg_idx]
    plaintext = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(target_ct) and keystream[pos] is not None:
            p_byte = target_ct[pos] ^ keystream[pos]
            plaintext.append(p_byte)
        else:
            # If keystream not known, try to recover it from other messages
            # using crib-dragging or frequency analysis
            # For now, we'll try a heuristic approach
            
            # Try XORing with other ciphertexts at same position
            # and looking for readable text patterns
            candidates = []
            for other_idx, other_ct in ct_map.items():
                if other_idx != target_msg_idx and pos < len(other_ct):
                    # XOR two ciphertexts: C1 XOR C2 = P1 XOR P2
                    xor_val = target_ct[pos] ^ other_ct[pos]
                    # Try common plaintext bytes (space, letters, etc.)
                    for guess in range(32, 127):  # printable ASCII
                        p_byte = xor_val ^ guess
                        if 32 <= p_byte < 127 or p_byte in [9, 10, 13]:
                            candidates.append(p_byte)
            
            if candidates:
                # Use most common candidate or middle value
                plaintext.append(sorted(candidates)[len(candidates)//2])
            else:
                plaintext.append(0)
    
    # Convert to hex
    result = bytes(plaintext).hex()
    
    print(json.dumps({"plaintext": result}))

if __name__ == "__main__":
    main()