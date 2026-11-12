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
    
    max_len = max(len(ct['data']) for ct in ciphertexts)
    keystream = [None] * max_len
    
    for kp in known_plaintexts:
        ct_data = next(ct['data'] for ct in ciphertexts if ct['index'] == kp['index'])
        plaintext = kp['data']
        offset = kp['offset']
        
        for i, p_byte in enumerate(plaintext):
            pos = offset + i
            if pos < len(ct_data):
                key_byte = ct_data[pos] ^ p_byte
                if keystream[pos] is None:
                    keystream[pos] = key_byte
                elif keystream[pos] != key_byte:
                    pass
    
    for pos in range(max_len):
        if keystream[pos] is None:
            for kp in known_plaintexts:
                ct1_data = next(ct['data'] for ct in ciphertexts if ct['index'] == kp['index'])
                if pos >= kp['offset'] and pos < kp['offset'] + len(kp['data']):
                    kp_pos = pos - kp['offset']
                    key_byte = ct1_data[pos] ^ kp['data'][kp_pos]
                    keystream[pos] = key_byte
                    break
    
    for pos in range(max_len):
        if keystream[pos] is None:
            for ct1 in ciphertexts:
                found = False
                for kp in known_plaintexts:
                    if kp['index'] == ct1['index'] and pos >= kp['offset'] and pos < kp['offset'] + len(kp['data']):
                        ct1_data = ct1['data']
                        kp_pos = pos - kp['offset']
                        key_byte = ct1_data[pos] ^ kp['data'][kp_pos]
                        keystream[pos] = key_byte
                        found = True
                        break
                if found:
                    break
    
    target_ct = next(ct['data'] for ct in ciphertexts if ct['index'] == target_index)
    
    plaintext_bytes = bytearray()
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(target_ct) and keystream[pos] is not None:
            plaintext_bytes.append(target_ct[pos] ^ keystream[pos])
        else:
            plaintext_bytes.append(0)
    
    result = {
        "plaintext": bytes_to_hex(plaintext_bytes)
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
