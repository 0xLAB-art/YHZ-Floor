import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    # Parse input
    ciphertexts = []
    for ct in instance['ciphertexts']:
        ciphertexts.append(bytes.fromhex(ct['data']))
    
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Extract keystream from known plaintexts
    # Assumption: stream cipher (XOR-based), reused keystream across messages
    keystreams = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext = bytes.fromhex(kp['data'])
        ciphertext = ciphertexts[msg_idx]
        
        # XOR ciphertext with plaintext to get keystream
        for i, p_byte in enumerate(plaintext):
            pos = offset + i
            if pos < len(ciphertext):
                k_byte = ciphertext[pos] ^ p_byte
                keystreams[pos] = k_byte
    
    # Check if we have enough keystream for the target
    target_start = target['offset']
    target_length = target['length']
    target_msg_idx = target['message_index']
    
    # Check coverage
    missing_positions = []
    for pos in range(target_start, target_start + target_length):
        if pos not in keystreams:
            missing_positions.append(pos)
    
    if missing_positions:
        result = {
            "status": "UNDERDETERMINED",
            "reason": f"Insufficient keystream coverage: missing {len(missing_positions)} of {target_length} required bytes"
        }
    else:
        # We have full keystream, decrypt target
        target_ciphertext = ciphertexts[target_msg_idx]
        plaintext_bytes = []
        
        for i in range(target_length):
            pos = target_start + i
            if pos < len(target_ciphertext):
                p_byte = target_ciphertext[pos] ^ keystreams[pos]
                plaintext_bytes.append(p_byte)
            else:
                # Ciphertext too short
                result = {
                    "status": "UNDERDETERMINED",
                    "reason": "Target extends beyond ciphertext length"
                }
                print(json.dumps(result))
                return
        
        plaintext_hex = bytes(plaintext_bytes).hex()
        result = {
            "status": "SOLVED",
            "plaintext": plaintext_hex
        }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()