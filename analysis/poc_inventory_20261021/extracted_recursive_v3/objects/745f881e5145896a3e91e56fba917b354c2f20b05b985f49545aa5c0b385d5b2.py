import json
import sys

def hex_to_bytes(hex_string):
    return bytes.fromhex(hex_string)

def bytes_to_hex(byte_data):
    return byte_data.hex()

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse the instance
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Find the ciphertexts
    ciphertexts = {}
    for ct in instance['ciphertexts']:
        ciphertexts[ct['message_index']] = hex_to_bytes(ct['data'])
    
    # Find the known plaintext
    known_plaintexts = {}
    for kp in instance['known_plaintexts']:
        known_plaintexts[kp['message_index']] = {
            'offset': kp['offset'],
            'data': hex_to_bytes(kp['data'])
        }
    
    # Find a known plaintext that overlaps with our target region
    # or can help us derive the keystream
    keystream = None
    
    for kp_msg_idx, kp_info in known_plaintexts.items():
        kp_offset = kp_info['offset']
        kp_data = kp_info['data']
        
        if kp_msg_idx in ciphertexts:
            # Recover keystream for this message
            ct = ciphertexts[kp_msg_idx]
            # keystream = plaintext ⊕ ciphertext
            ks = xor_bytes(kp_data, ct[kp_offset:kp_offset + len(kp_data)])
            
            # Store the keystream with its offset
            if keystream is None:
                keystream = {}
            
            for i, b in enumerate(ks):
                keystream[kp_offset + i] = b
    
    # Now decrypt the target using the recovered keystream
    target_ct = ciphertexts[target_msg_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if keystream and pos in keystream:
            # plaintext = ciphertext ⊕ keystream
            pt_byte = target_ct[pos] ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # Should not happen if we have sufficient known plaintext
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    # Output the result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()