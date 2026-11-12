import json
import sys

def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

def bytes_to_hex(b):
    return b.hex()

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    ciphertexts = {}
    for ct in instance['ciphertexts']:
        ciphertexts[ct['message_index']] = hex_to_bytes(ct['data'])
    
    known_plaintexts = {}
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        offset = kp['offset']
        data = hex_to_bytes(kp['data'])
        if msg_idx not in known_plaintexts:
            known_plaintexts[msg_idx] = {}
        for i, byte in enumerate(data):
            known_plaintexts[msg_idx][offset + i] = byte
    
    # Derive keystream bytes from known plaintexts
    keystream = {}
    for msg_idx, positions in known_plaintexts.items():
        ct = ciphertexts[msg_idx]
        for pos, pt_byte in positions.items():
            if pos < len(ct):
                keystream[pos] = ct[pos] ^ pt_byte
    
    # Decrypt target using derived keystream
    target_ct = ciphertexts[target_msg_idx]
    plaintext = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ct):
            pt_byte = target_ct[pos] ^ keystream[pos]
            plaintext.append(pt_byte)
        else:
            # If we don't have the keystream byte, we can't decrypt
            # This shouldn't happen if the instance is solvable
            plaintext.append(0)
    
    result = {
        "plaintext": bytes(plaintext).hex()
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
