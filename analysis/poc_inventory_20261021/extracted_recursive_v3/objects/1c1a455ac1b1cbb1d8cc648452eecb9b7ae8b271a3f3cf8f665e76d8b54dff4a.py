import sys
import json

def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

def bytes_to_hex(b):
    return b.hex()

def xor_bytes(b1, b2):
    return bytes(a ^ b for a, b in zip(b1, b2))

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = []
    for ct in instance['ciphertexts']:
        ciphertexts.append({
            'data': hex_to_bytes(ct['data']),
            'index': ct['message_index']
        })
    
    known_plaintexts = []
    for kp in instance['known_plaintexts']:
        known_plaintexts.append({
            'data': hex_to_bytes(kp['data']),
            'index': kp['message_index'],
            'offset': kp['offset']
        })
    
    target_index = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    # Find the ciphertext for the target
    target_ct = None
    for ct in ciphertexts:
        if ct['index'] == target_index:
            target_ct = ct['data']
            break
    
    # Recover keystream bytes using known plaintexts
    max_len = max(len(ct['data']) for ct in ciphertexts)
    keystream = [None] * max_len
    
    for kp in known_plaintexts:
        msg_index = kp['index']
        offset = kp['offset']
        plaintext = kp['data']
        
        # Find the ciphertext for this message
        ct_data = None
        for ct in ciphertexts:
            if ct['index'] == msg_index:
                ct_data = ct['data']
                break
        
        if ct_data:
            # Recover keystream: keystream = ciphertext XOR plaintext
            for i, pt_byte in enumerate(plaintext):
                pos = offset + i
                if pos < len(ct_data):
                    ks_byte = ct_data[pos] ^ pt_byte
                    keystream[pos] = ks_byte
    
    # Decrypt the target using the recovered keystream
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(target_ct) and keystream[pos] is not None:
            pt_byte = target_ct[pos] ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # If we don't have keystream, try to infer from other ciphertexts
            # For now, use 0 as fallback (should not happen with enough known plaintexts)
            plaintext_bytes.append(0)
    
    result = {
        'plaintext': bytes(plaintext_bytes).hex()
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()