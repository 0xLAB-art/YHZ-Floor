import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Convert hex ciphertexts to bytes
    ct_bytes = {}
    for ct in ciphertexts:
        ct_bytes[ct['message_index']] = bytes.fromhex(ct['data'])
    
    # Convert known plaintexts to bytes
    kp_bytes = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        data = bytes.fromhex(kp['data'])
        if msg_idx not in kp_bytes:
            kp_bytes[msg_idx] = {}
        for i, b in enumerate(data):
            kp_bytes[msg_idx][offset + i] = b
    
    # This is a stream cipher reuse attack (XOR with same keystream)
    # C_i = P_i XOR K
    # If we know P_i at position j, we can find K[j] = C_i[j] XOR P_i[j]
    # Then P_target[j] = C_target[j] XOR K[j]
    
    # Recover keystream bytes
    keystream = {}
    for msg_idx, positions in kp_bytes.items():
        for pos, pt_byte in positions.items():
            ct_byte = ct_bytes[msg_idx][pos]
            keystream[pos] = ct_byte ^ pt_byte
    
    # Decrypt target message
    target_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext = bytearray()
    for i in range(target_offset, target_offset + target_length):
        if i in keystream:
            pt_byte = ct_bytes[target_idx][i] ^ keystream[i]
            plaintext.append(pt_byte)
        else:
            # Try to recover keystream from other messages
            # We can use crib dragging or statistical analysis
            # For now, try common patterns
            plaintext.append(0)
    
    # Try to fill missing bytes using crib dragging
    # XOR two ciphertexts: C1 XOR C2 = P1 XOR P2
    for i in range(target_offset, target_offset + target_length):
        if i not in keystream and i < len(ct_bytes[target_idx]):
            # Try to find this position in keystream using other ciphertexts
            for msg_idx in ct_bytes:
                if msg_idx != target_idx and i < len(ct_bytes[msg_idx]):
                    if msg_idx in kp_bytes and i in kp_bytes[msg_idx]:
                        keystream[i] = ct_bytes[msg_idx][i] ^ kp_bytes[msg_idx][i]
                        plaintext[i - target_offset] = ct_bytes[target_idx][i] ^ keystream[i]
                        break
    
    result = {
        "plaintext": plaintext.hex()
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()