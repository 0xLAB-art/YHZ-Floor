import sys
import json

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Convert ciphertexts to bytes
    ct_bytes = {}
    for ct in ciphertexts:
        ct_bytes[ct['message_index']] = bytes.fromhex(ct['data'])
    
    # Build known plaintext dictionary
    known = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        data = bytes.fromhex(kp['data'])
        if msg_idx not in known:
            known[msg_idx] = {}
        for i, byte in enumerate(data):
            known[msg_idx][offset + i] = byte
    
    # Recover keystream
    keystream = {}
    for msg_idx in known:
        if msg_idx in ct_bytes:
            for pos, pt_byte in known[msg_idx].items():
                ct_byte = ct_bytes[msg_idx][pos]
                keystream[pos] = ct_byte ^ pt_byte
    
    # Decrypt target using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and target_msg_idx in ct_bytes:
            ct_byte = ct_bytes[target_msg_idx][pos]
            pt_byte = ct_byte ^ keystream[pos]
            plaintext.append(pt_byte)
        else:
            # Fallback: no keystream known for this position
            plaintext.append(0)
    
    result = {
        "plaintext": bytes(plaintext).hex()
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()