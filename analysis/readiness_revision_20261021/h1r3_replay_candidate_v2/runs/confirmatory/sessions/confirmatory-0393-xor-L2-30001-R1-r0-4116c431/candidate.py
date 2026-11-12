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
        idx = ct['message_index']
        ct_data[idx] = bytes.fromhex(ct['data'])
    
    # Parse known plaintexts
    known = {}
    for kp in known_plaintexts:
        idx = kp['message_index']
        offset = kp['offset']
        data = bytes.fromhex(kp['data'])
        if idx not in known:
            known[idx] = {}
        for i, byte in enumerate(data):
            known[idx][offset + i] = byte
    
    # This is a stream cipher reuse attack (same keystream)
    # ct[i] = pt[i] XOR key[i]
    # If we know pt[i] for some message, we can recover key[i]
    # Then decrypt other messages at that position
    
    target_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Recover keystream bytes where we have known plaintexts
    keystream = {}
    for msg_idx in known:
        for pos in known[msg_idx]:
            pt_byte = known[msg_idx][pos]
            ct_byte = ct_data[msg_idx][pos]
            key_byte = pt_byte ^ ct_byte
            keystream[pos] = key_byte
    
    # Decrypt target message using recovered keystream
    result = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            # We have the keystream byte, decrypt directly
            ct_byte = ct_data[target_idx][pos]
            pt_byte = ct_byte ^ keystream[pos]
            result.append(pt_byte)
        else:
            # We don't have this keystream byte
            # Try to infer from other messages if possible
            # For now, we'll use 0x00 as placeholder (this shouldn't happen with enough knowns)
            result.append(0)
    
    plaintext_hex = bytes(result).hex()
    print(json.dumps({"plaintext": plaintext_hex}))

if __name__ == "__main__":
    main()
