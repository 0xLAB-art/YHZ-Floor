import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Parse ciphertexts
    ct_data = {}
    for ct in ciphertexts:
        msg_idx = ct['message_index']
        ct_data[msg_idx] = bytes.fromhex(ct['data'])
    
    # Build known plaintext map
    known = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        data = bytes.fromhex(kp['data'])
        if msg_idx not in known:
            known[msg_idx] = {}
        for i, byte in enumerate(data):
            known[msg_idx][offset + i] = byte
    
    # Recover keystream using known plaintexts
    keystream = {}
    for msg_idx in known:
        if msg_idx in ct_data:
            for pos, pt_byte in known[msg_idx].items():
                if pos < len(ct_data[msg_idx]):
                    keystream[pos] = ct_data[msg_idx][pos] ^ pt_byte
    
    # Decrypt target using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and target_msg_idx in ct_data and pos < len(ct_data[target_msg_idx]):
            pt_byte = ct_data[target_msg_idx][pos] ^ keystream[pos]
            plaintext.append(pt_byte)
        else:
            # Try to recover keystream from crib-dragging
            # Use frequency analysis or common patterns
            plaintext.append(0)
    
    result = {
        "plaintext": bytes(plaintext).hex()
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()