import sys
import json
import base64

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse ciphertexts
    ciphertexts = {}
    for ct in instance['ciphertexts']:
        idx = ct['message_index']
        data = base64.b64decode(ct['data'])
        ciphertexts[idx] = data
    
    # Parse known plaintexts
    known_plaintexts = {}
    for kp in instance['known_plaintexts']:
        idx = kp['message_index']
        offset = kp['offset']
        data = base64.b64decode(kp['data'])
        if idx not in known_plaintexts:
            known_plaintexts[idx] = {}
        known_plaintexts[idx][offset] = data
    
    # Parse target
    target_msg_idx = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    # Get the ciphertext we want to decrypt
    target_ciphertext = ciphertexts[target_msg_idx]
    
    # Find a known plaintext we can use (should be from a different message)
    # Stream cipher reuse: if C0 = P0 XOR K and C1 = P1 XOR K
    # then P1 = C1 XOR C0 XOR P0
    
    for known_idx, offsets in known_plaintexts.items():
        if known_idx == target_msg_idx:
            continue
            
        for known_offset, known_plaintext in offsets.items():
            known_ciphertext = ciphertexts[known_idx]
            
            # Extract the relevant portions
            known_ct_chunk = known_ciphertext[known_offset:known_offset + len(known_plaintext)]
            target_ct_chunk = target_ciphertext[target_offset:target_offset + target_length]
            
            # XOR to recover the target plaintext
            # P_target = C_target XOR C_known XOR P_known
            plaintext_bytes = bytes(
                target_ct_chunk[i] ^ known_ct_chunk[i] ^ known_plaintext[i]
                for i in range(min(len(target_ct_chunk), len(known_ct_chunk), len(known_plaintext)))
            )
            
            # Convert to hex
            plaintext_hex = plaintext_bytes.hex()
            
            result = {"plaintext": plaintext_hex}
            print(json.dumps(result))
            return

if __name__ == "__main__":
    main()