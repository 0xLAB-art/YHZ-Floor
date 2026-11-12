import sys
import json
import base64

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode all ciphertexts
    ciphertexts = []
    for ct in instance['ciphertexts']:
        ciphertexts.append(base64.b64decode(ct['data']))
    
    # Parse known plaintexts
    known = {}
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = base64.b64decode(kp['data'])
        
        if msg_idx not in known:
            known[msg_idx] = {}
        
        for i, byte in enumerate(plaintext_bytes):
            known[msg_idx][offset + i] = byte
    
    # Extract keystream from known plaintexts
    keystream = {}
    for msg_idx in known:
        for pos, pt_byte in known[msg_idx].items():
            ct_byte = ciphertexts[msg_idx][pos]
            ks_byte = ct_byte ^ pt_byte
            
            if pos in keystream and keystream[pos] != ks_byte:
                # Conflict - should not happen in a valid instance
                pass
            keystream[pos] = ks_byte
    
    # Decrypt target using recovered keystream
    target_msg_idx = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    plaintext = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            pt_byte = ciphertexts[target_msg_idx][pos] ^ keystream[pos]
            plaintext.append(pt_byte)
        else:
            # No keystream recovered for this position
            # Try to infer from context or use frequency analysis
            plaintext.append(0)
    
    plaintext_hex = bytes(plaintext).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()