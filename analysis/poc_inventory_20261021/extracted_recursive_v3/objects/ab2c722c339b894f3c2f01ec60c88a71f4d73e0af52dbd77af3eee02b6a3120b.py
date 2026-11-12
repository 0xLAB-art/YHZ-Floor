import sys
import json

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
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert ciphertexts to bytes
    ciphertext_data = []
    for ct in ciphertexts:
        ciphertext_data.append({
            'data': hex_to_bytes(ct['data']),
            'message_index': ct['message_index']
        })
    
    # Find the maximum length needed for keystream
    max_length = target['offset'] + target['length']
    
    # Recover keystream using known plaintexts
    keystream = [None] * max_length
    
    for kp in known_plaintexts:
        plaintext_bytes = hex_to_bytes(kp['data'])
        message_index = kp['message_index']
        offset = kp['offset']
        
        # Find the corresponding ciphertext
        ciphertext = None
        for ct in ciphertext_data:
            if ct['message_index'] == message_index:
                ciphertext = ct['data']
                break
        
        if ciphertext is None:
            continue
        
        # Recover keystream bytes at this position
        for i, p_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ciphertext):
                c_byte = ciphertext[pos]
                k_byte = p_byte ^ c_byte
                keystream[pos] = k_byte
    
    # Find target ciphertext
    target_ciphertext = None
    for ct in ciphertext_data:
        if ct['message_index'] == target['message_index']:
            target_ciphertext = ct['data']
            break
    
    # Decrypt target using recovered keystream
    plaintext_bytes = []
    for i in range(target['length']):
        pos = target['offset'] + i
        if keystream[pos] is not None and pos < len(target_ciphertext):
            p_byte = target_ciphertext[pos] ^ keystream[pos]
            plaintext_bytes.append(p_byte)
        else:
            # This shouldn't happen if we have enough known plaintexts
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    # Output result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()