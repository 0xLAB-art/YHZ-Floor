import json
import sys

def hex_to_bytes(h):
    return bytes.fromhex(h)

def bytes_to_hex(b):
    return b.hex()

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = []
    for ct in instance['ciphertexts']:
        ciphertexts.append({
            'data': hex_to_bytes(ct['data']),
            'index': ct['message_index']
        })
    
    known = []
    for kp in instance['known_plaintexts']:
        known.append({
            'data': hex_to_bytes(kp['data']),
            'index': kp['message_index'],
            'offset': kp['offset']
        })
    
    target_index = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    # Recover keystream bytes using known plaintexts
    keystream = {}
    
    for kp in known:
        msg_idx = kp['index']
        offset = kp['offset']
        plaintext = kp['data']
        
        # Find the ciphertext for this message
        ciphertext = None
        for ct in ciphertexts:
            if ct['index'] == msg_idx:
                ciphertext = ct['data']
                break
        
        if ciphertext:
            # Recover keystream: K = P ⊕ C
            for i, p_byte in enumerate(plaintext):
                pos = offset + i
                if pos < len(ciphertext):
                    k_byte = p_byte ^ ciphertext[pos]
                    keystream[pos] = k_byte
    
    # Find target ciphertext
    target_ciphertext = None
    for ct in ciphertexts:
        if ct['index'] == target_index:
            target_ciphertext = ct['data']
            break
    
    # Decrypt target using recovered keystream
    result = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ciphertext):
            p_byte = target_ciphertext[pos] ^ keystream[pos]
            result.append(p_byte)
        else:
            # If we don't have the keystream byte, we can't decrypt
            result.append(0)
    
    plaintext_hex = bytes_to_hex(bytes(result))
    
    output = {"plaintext": plaintext_hex}
    print(json.dumps(output))

if __name__ == "__main__":
    main()