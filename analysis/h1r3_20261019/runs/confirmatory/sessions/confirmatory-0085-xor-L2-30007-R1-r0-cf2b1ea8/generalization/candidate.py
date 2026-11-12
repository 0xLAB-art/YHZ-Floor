import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Convert hex strings to bytes
    ct_bytes = {}
    for ct in ciphertexts:
        ct_bytes[ct['message_index']] = bytes.fromhex(ct['data'])
    
    # Parse known plaintexts
    known = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        data = bytes.fromhex(kp['data'])
        if msg_idx not in known:
            known[msg_idx] = {}
        for i, b in enumerate(data):
            known[msg_idx][offset + i] = b
    
    # Stream cipher (likely XOR-based): C = P XOR K
    # If we know P and C, we can recover K: K = P XOR C
    # Then use K to decrypt target
    
    # Recover keystream bytes where we have known plaintexts
    keystream = {}
    for msg_idx in known:
        for pos, pt_byte in known[msg_idx].items():
            if msg_idx in ct_bytes and pos < len(ct_bytes[msg_idx]):
                ct_byte = ct_bytes[msg_idx][pos]
                keystream[pos] = pt_byte ^ ct_byte
    
    # Decrypt target message
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and target_msg_idx in ct_bytes and pos < len(ct_bytes[target_msg_idx]):
            ct_byte = ct_bytes[target_msg_idx][pos]
            pt_byte = ct_byte ^ keystream[pos]
            plaintext.append(pt_byte)
        else:
            # If keystream not known at this position, we can't decrypt
            # Try cribbing or statistical attacks
            # For now, use 0x00 as fallback (should not happen with sufficient known plaintexts)
            plaintext.append(0)
    
    result = {
        "plaintext": bytes(plaintext).hex()
    }
    print(json.dumps(result))

if __name__ == '__main__':
    main()
