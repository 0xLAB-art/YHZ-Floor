import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Convert hex ciphertexts to bytes
    ct_bytes = {}
    for ct in ciphertexts:
        ct_bytes[ct['message_index']] = bytes.fromhex(ct['data'])
    
    # Build known plaintext mapping: (message_index, offset) -> plaintext_bytes
    known = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_data = bytes.fromhex(kp['data'])
        for i, b in enumerate(pt_data):
            known[(msg_idx, offset + i)] = b
    
    # XOR stream cipher attack: C = P XOR K
    # If we know P for some position, we can recover K at that position: K = P XOR C
    # Then we can decrypt other messages at the same position: P' = C' XOR K
    
    # Build keystream from known plaintexts
    keystream = {}
    for (msg_idx, pos), pt_byte in known.items():
        ct_byte = ct_bytes[msg_idx][pos]
        key_byte = pt_byte ^ ct_byte
        if pos in keystream and keystream[pos] != key_byte:
            # Inconsistency - shouldn't happen if same key used
            pass
        keystream[pos] = key_byte
    
    # Decrypt target message
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            # Decrypt using known keystream
            ct_byte = ct_bytes[target_msg_idx][pos]
            pt_byte = ct_byte ^ keystream[pos]
            plaintext.append(pt_byte)
        else:
            # No keystream known at this position
            # Try to use crib-dragging or known plaintext from other messages
            plaintext.append(0)
    
    result = {
        "plaintext": bytes(plaintext).hex()
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
