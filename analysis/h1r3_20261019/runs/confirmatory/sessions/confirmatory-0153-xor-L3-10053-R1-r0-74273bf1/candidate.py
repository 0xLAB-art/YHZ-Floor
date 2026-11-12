import sys
import json

def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

def bytes_to_hex(b):
    return b.hex()

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Convert ciphertexts to bytes
    ct_bytes = {}
    for ct in ciphertexts:
        ct_bytes[ct['message_index']] = hex_to_bytes(ct['data'])
    
    # Build known plaintext map: (message_index, offset) -> plaintext_bytes
    known_map = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_data = hex_to_bytes(kp['data'])
        for i, byte in enumerate(pt_data):
            known_map[(msg_idx, offset + i)] = byte
    
    # Recover keystream at positions where we have known plaintext
    keystream = {}
    for (msg_idx, pos), pt_byte in known_map.items():
        if msg_idx in ct_bytes and pos < len(ct_bytes[msg_idx]):
            ct_byte = ct_bytes[msg_idx][pos]
            keystream[pos] = ct_byte ^ pt_byte
    
    # Decrypt target message using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    if target_msg_idx not in ct_bytes:
        print(json.dumps({"plaintext": "00" * target_length}))
        return
    
    target_ct = ct_bytes[target_msg_idx]
    plaintext = []
    
    for i in range(target_length):
        pos = target_offset + i
        
        # Check if we already know the plaintext at this position
        if (target_msg_idx, pos) in known_map:
            plaintext.append(known_map[(target_msg_idx, pos)])
        # Check if we have keystream for this position
        elif pos in keystream and pos < len(target_ct):
            ct_byte = target_ct[pos]
            pt_byte = ct_byte ^ keystream[pos]
            plaintext.append(pt_byte)
        # Try to recover keystream from crib-dragging if possible
        else:
            # Try to find another message with known plaintext at this position
            recovered = False
            if pos < len(target_ct):
                for other_idx in ct_bytes:
                    if other_idx != target_msg_idx and (other_idx, pos) in known_map:
                        if pos < len(ct_bytes[other_idx]):
                            other_ct = ct_bytes[other_idx][pos]
                            other_pt = known_map[(other_idx, pos)]
                            ks = other_ct ^ other_pt
                            keystream[pos] = ks
                            pt_byte = target_ct[pos] ^ ks
                            plaintext.append(pt_byte)
                            recovered = True
                            break
            
            if not recovered:
                plaintext.append(0)
    
    result = bytes_to_hex(bytes(plaintext))
    print(json.dumps({"plaintext": result}))

if __name__ == "__main__":
    main()
