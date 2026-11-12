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
    
    # Build known plaintext mapping: position -> {message_index: plaintext_byte}
    known = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = bytes.fromhex(kp['data'])
        for i, byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos not in known:
                known[pos] = {}
            known[pos][msg_idx] = byte
    
    # For stream cipher with reused key: C_i = P_i XOR K
    # If we know P_i for message i at position pos, we can recover K[pos] = C_i XOR P_i
    # Then for any other message j at same position: P_j = C_j XOR K[pos]
    
    # Recover keystream bytes where we have known plaintexts
    keystream = {}
    for pos in known:
        for msg_idx in known[pos]:
            if msg_idx in ct_bytes and pos < len(ct_bytes[msg_idx]):
                keystream[pos] = ct_bytes[msg_idx][pos] ^ known[pos][msg_idx]
                break
    
    # Decrypt target message using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and target_msg_idx in ct_bytes and pos < len(ct_bytes[target_msg_idx]):
            plaintext_byte = ct_bytes[target_msg_idx][pos] ^ keystream[pos]
            plaintext_bytes.append(plaintext_byte)
        else:
            # If we don't have keystream for this position, we can't decrypt
            # This shouldn't happen if the instance is solvable
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()