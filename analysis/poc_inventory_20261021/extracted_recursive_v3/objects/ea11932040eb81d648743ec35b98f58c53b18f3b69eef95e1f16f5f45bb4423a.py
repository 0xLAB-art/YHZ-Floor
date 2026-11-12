import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    # Parse input
    ciphertexts = [bytes.fromhex(ct['data']) for ct in instance['ciphertexts']]
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Extract known plaintext information
    known = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        data = bytes.fromhex(kp['data'])
        if msg_idx not in known:
            known[msg_idx] = {}
        for i, byte in enumerate(data):
            known[msg_idx][offset + i] = byte
    
    # For stream cipher (likely XOR-based), we can recover keystream from known plaintext
    # If C = P XOR K, then K = C XOR P
    keystream = {}
    for msg_idx, positions in known.items():
        for pos, plaintext_byte in positions.items():
            ciphertext_byte = ciphertexts[msg_idx][pos]
            keystream[pos] = ciphertext_byte ^ plaintext_byte
    
    # Check if we have enough keystream to decrypt the target
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Verify we have keystream for all target positions
    missing_positions = []
    for pos in range(target_offset, target_offset + target_length):
        if pos not in keystream:
            missing_positions.append(pos)
    
    if missing_positions:
        result = {
            "status": "UNDERDETERMINED",
            "reason": f"Insufficient known plaintext to recover keystream at {len(missing_positions)} positions needed for target decryption"
        }
    else:
        # We can decrypt the target
        target_plaintext = bytearray()
        for pos in range(target_offset, target_offset + target_length):
            ciphertext_byte = ciphertexts[target_msg_idx][pos]
            plaintext_byte = ciphertext_byte ^ keystream[pos]
            target_plaintext.append(plaintext_byte)
        
        result = {
            "status": "SOLVED",
            "plaintext": target_plaintext.hex()
        }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()