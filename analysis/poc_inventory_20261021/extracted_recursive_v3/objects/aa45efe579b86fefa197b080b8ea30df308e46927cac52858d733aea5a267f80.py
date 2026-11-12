import sys
import json

def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

def bytes_to_hex(b):
    return b.hex()

def xor_bytes(b1, b2):
    return bytes(x ^ y for x, y in zip(b1, b2))

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse data
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
    
    target = instance['target']
    target_index = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Get target ciphertext
    target_ct = None
    for ct in ciphertexts:
        if ct['index'] == target_index:
            target_ct = ct['data']
            break
    
    if target_ct is None:
        print(json.dumps({"status": "UNDERDETERMINED", "reason": "Target ciphertext not found"}))
        return
    
    # Check if target region is within ciphertext bounds
    if target_offset + target_length > len(target_ct):
        print(json.dumps({"status": "UNDERDETERMINED", "reason": "Target region exceeds ciphertext length"}))
        return
    
    # Recover keystream at known plaintext positions
    keystream = {}
    for kp in known_plaintexts:
        msg_idx = kp['index']
        offset = kp['offset']
        pt = kp['data']
        
        # Find corresponding ciphertext
        ct = None
        for c in ciphertexts:
            if c['index'] == msg_idx:
                ct = c['data']
                break
        
        if ct is None:
            continue
        
        # Recover keystream: key = plaintext XOR ciphertext
        for i, pt_byte in enumerate(pt):
            pos = offset + i
            if pos < len(ct):
                key_byte = pt_byte ^ ct[pos]
                keystream[pos] = key_byte
    
    # Check if we have keystream for the entire target region
    target_start = target_offset
    target_end = target_offset + target_length
    
    can_decrypt = True
    for pos in range(target_start, target_end):
        if pos not in keystream:
            can_decrypt = False
            break
    
    if not can_decrypt:
        # Count how much we can recover
        covered = sum(1 for pos in range(target_start, target_end) if pos in keystream)
        print(json.dumps({
            "status": "UNDERDETERMINED",
            "reason": f"Only {covered}/{target_length} bytes of keystream recovered for target region"
        }))
        return
    
    # Decrypt target
    target_plaintext = bytearray()
    for pos in range(target_start, target_end):
        ct_byte = target_ct[pos]
        key_byte = keystream[pos]
        pt_byte = ct_byte ^ key_byte
        target_plaintext.append(pt_byte)
    
    # This shouldn't happen if we reach here, but as a fallback
    print(json.dumps({
        "status": "UNDERDETERMINED",
        "reason": "Insufficient keystream coverage"
    }))

if __name__ == "__main__":
    main()