import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Build a map of ciphertext data by message_index
    ct_map = {}
    for ct in ciphertexts:
        ct_map[ct['message_index']] = bytes.fromhex(ct['data'])
    
    # Build a map of known plaintext bytes by (message_index, offset)
    known_map = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        data = bytes.fromhex(kp['data'])
        for i, b in enumerate(data):
            known_map[(msg_idx, offset + i)] = b
    
    # This looks like a stream cipher reuse attack (same keystream used for multiple messages)
    # For stream cipher: C = P XOR K, where K is the keystream
    # If we know P for some position in one message, we can recover K at that position
    # Then use K to decrypt other messages at the same position
    
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Recover keystream bytes where we have known plaintexts
    keystream = {}
    for (msg_idx, offset), pt_byte in known_map.items():
        if msg_idx in ct_map and offset < len(ct_map[msg_idx]):
            ct_byte = ct_map[msg_idx][offset]
            keystream[offset] = ct_byte ^ pt_byte
    
    # Decrypt the target message using the recovered keystream
    result = []
    target_ct = ct_map[target_msg_idx]
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ct):
            pt_byte = target_ct[pos] ^ keystream[pos]
            result.append(pt_byte)
        else:
            # If we don't have keystream for this position, we can't decrypt it
            # This shouldn't happen if the instance is solvable
            result.append(0)
    
    plaintext_hex = bytes(result).hex()
    print(json.dumps({"plaintext": plaintext_hex}))

if __name__ == '__main__':
    main()
