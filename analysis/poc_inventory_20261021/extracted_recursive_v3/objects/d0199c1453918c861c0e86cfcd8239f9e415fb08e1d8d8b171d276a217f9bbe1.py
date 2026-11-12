import sys
import json

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert hex ciphertexts to bytes
    ct_bytes = []
    for ct in ciphertexts:
        ct_bytes.append(bytes.fromhex(ct['data']))
    
    # This appears to be a many-time pad attack
    # XOR reuse allows us to recover the keystream at known positions
    
    # Reconstruct keystream from known plaintexts
    max_len = max(len(ct) for ct in ct_bytes)
    keystream = [None] * max_len
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = bytes.fromhex(kp['data'])
        
        for i, p_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ct_bytes[msg_idx]):
                k_byte = ct_bytes[msg_idx][pos] ^ p_byte
                keystream[pos] = k_byte
    
    # Extract target plaintext using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    result = []
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(keystream) and keystream[pos] is not None:
            if pos < len(ct_bytes[target_msg_idx]):
                p_byte = ct_bytes[target_msg_idx][pos] ^ keystream[pos]
                result.append(p_byte)
            else:
                result.append(0)
        else:
            result.append(0)
    
    plaintext_hex = bytes(result).hex()
    
    print(json.dumps({"plaintext": plaintext_hex}))

if __name__ == "__main__":
    main()