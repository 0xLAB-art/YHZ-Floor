import sys
import json

def hex_to_bytes(h):
    return bytes.fromhex(h)

def bytes_to_hex(b):
    return b.hex()

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Convert ciphertexts to bytes
    ct_data = {}
    for ct in ciphertexts:
        ct_data[ct['message_index']] = hex_to_bytes(ct['data'])
    
    # Find the maximum length needed
    max_len = max(len(ct) for ct in ct_data.values())
    
    # Initialize keystream as unknown
    keystream = [None] * max_len
    
    # Use known plaintexts to recover keystream
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = hex_to_bytes(kp['data'])
        
        ct = ct_data[msg_idx]
        
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ct):
                # keystream[pos] = ciphertext[pos] XOR plaintext[pos]
                key_byte = ct[pos] ^ pt_byte
                
                if keystream[pos] is None:
                    keystream[pos] = key_byte
                elif keystream[pos] != key_byte:
                    # Consistency check - shouldn't happen with valid data
                    pass
    
    # Iteratively propagate knowledge across messages
    # If we know plaintext at position i for message A, and keystream at position i,
    # we can derive plaintext for all other messages at position i
    changed = True
    iterations = 0
    max_iterations = 100
    
    # Track known plaintexts for each message
    known_pt = {}
    for msg_idx in ct_data:
        known_pt[msg_idx] = [None] * len(ct_data[msg_idx])
    
    # Initialize with given known plaintexts
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = hex_to_bytes(kp['data'])
        
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(known_pt[msg_idx]):
                known_pt[msg_idx][pos] = pt_byte
    
    while changed and iterations < max_iterations:
        changed = False
        iterations += 1
        
        # If we know keystream at a position, derive plaintext for all messages
        for pos in range(max_len):
            if keystream[pos] is not None:
                for msg_idx in ct_data:
                    ct = ct_data[msg_idx]
                    if pos < len(ct) and known_pt[msg_idx][pos] is None:
                        known_pt[msg_idx][pos] = ct[pos] ^ keystream[pos]
                        changed = True
        
        # If we know plaintext for any message at a position, derive keystream
        for msg_idx in ct_data:
            ct = ct_data[msg_idx]
            for pos in range(len(ct)):
                if known_pt[msg_idx][pos] is not None and keystream[pos] is None:
                    keystream[pos] = ct[pos] ^ known_pt[msg_idx][pos]
                    changed = True
    
    # Extract target plaintext
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    result_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if known_pt[target_msg_idx][pos] is not None:
            result_bytes.append(known_pt[target_msg_idx][pos])
        else:
            # Shouldn't happen if we have enough known plaintexts
            result_bytes.append(0)
    
    result_hex = bytes_to_hex(bytes(result_bytes))
    
    print(json.dumps({"plaintext": result_hex}))

if __name__ == '__main__':
    main()