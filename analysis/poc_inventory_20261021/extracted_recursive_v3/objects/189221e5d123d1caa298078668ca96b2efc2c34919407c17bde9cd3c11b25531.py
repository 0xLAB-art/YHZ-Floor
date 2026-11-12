import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Convert hex strings to byte arrays
    ct_bytes = []
    for ct in ciphertexts:
        ct_bytes.append(bytes.fromhex(ct['data']))
    
    # Build known plaintext mapping: {message_index: {offset: plaintext_bytes}}
    known = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_bytes = bytes.fromhex(kp['data'])
        if msg_idx not in known:
            known[msg_idx] = {}
        for i, b in enumerate(pt_bytes):
            known[msg_idx][offset + i] = b
    
    # Extract keystream bytes from known plaintexts
    # For stream cipher: C = P XOR K, so K = C XOR P
    keystream = {}
    for msg_idx in known:
        for offset, pt_byte in known[msg_idx].items():
            ct_byte = ct_bytes[msg_idx][offset]
            keystream[offset] = ct_byte ^ pt_byte
    
    # Decrypt target message using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            # We have the keystream byte, decrypt
            ct_byte = ct_bytes[target_msg_idx][pos]
            pt_byte = ct_byte ^ keystream[pos]
            plaintext.append(pt_byte)
        else:
            # Try to recover keystream from crib-dragging
            # XOR two ciphertexts to get P1 XOR P2
            # If we know P1, we can get P2, then recover keystream
            recovered = False
            for other_idx in range(len(ct_bytes)):
                if other_idx == target_msg_idx:
                    continue
                if other_idx in known and pos in known[other_idx]:
                    # We know plaintext at this position in another message
                    ct1 = ct_bytes[target_msg_idx][pos]
                    ct2 = ct_bytes[other_idx][pos]
                    pt2 = known[other_idx][pos]
                    # ct1 = pt1 XOR k, ct2 = pt2 XOR k
                    # ct1 XOR ct2 = pt1 XOR pt2
                    # pt1 = (ct1 XOR ct2) XOR pt2
                    pt_byte = (ct1 ^ ct2) ^ pt2
                    plaintext.append(pt_byte)
                    # Also recover keystream for future use
                    keystream[pos] = ct1 ^ pt_byte
                    recovered = True
                    break
            
            if not recovered:
                # Should not happen if instance is solvable
                plaintext.append(0)
    
    result = {
        "plaintext": bytes(plaintext).hex()
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
