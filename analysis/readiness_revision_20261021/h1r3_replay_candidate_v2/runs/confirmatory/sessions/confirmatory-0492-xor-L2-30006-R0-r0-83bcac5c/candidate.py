import json
import sys

def hex_to_bytes(h):
    return bytes.fromhex(h)

def bytes_to_hex(b):
    return b.hex()

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse input
    ciphertexts = {}
    for ct in instance['ciphertexts']:
        ciphertexts[ct['message_index']] = hex_to_bytes(ct['data'])
    
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Determine keystream length (maximum ciphertext length)
    max_len = max(len(ct) for ct in ciphertexts.values())
    
    # Recover keystream using known plaintexts
    keystream = [None] * max_len
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = hex_to_bytes(kp['data'])
        ciphertext = ciphertexts[msg_idx]
        
        # Recover keystream at this position
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ciphertext):
                key_byte = ciphertext[pos] ^ pt_byte
                keystream[pos] = key_byte
    
    # Decrypt target using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ciphertext = ciphertexts[target_msg_idx]
    plaintext = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(target_ciphertext) and keystream[pos] is not None:
            pt_byte = target_ciphertext[pos] ^ keystream[pos]
            plaintext.append(pt_byte)
        else:
            # This shouldn't happen if we have enough known plaintext
            plaintext.append(0)
    
    plaintext_hex = bytes_to_hex(bytes(plaintext))
    
    # Output result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
