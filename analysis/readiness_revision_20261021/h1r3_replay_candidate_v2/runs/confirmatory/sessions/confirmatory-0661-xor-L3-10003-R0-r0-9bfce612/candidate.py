import sys
import json

def hex_decode(s):
    return bytes.fromhex(s)

def hex_encode(b):
    return b.hex()

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
        ct_bytes.append(hex_decode(ct['data']))
    
    # Recover keystream bytes from known plaintexts
    # In a stream cipher: C = P XOR K, so K = P XOR C
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext = hex_decode(kp['data'])
        
        ciphertext = ct_bytes[msg_idx]
        
        # Extract keystream bytes
        for i, p_byte in enumerate(plaintext):
            pos = offset + i
            if pos < len(ciphertext):
                k_byte = p_byte ^ ciphertext[pos]
                keystream[pos] = k_byte
    
    # Check if we can decrypt the target
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ciphertext = ct_bytes[target_msg_idx]
    
    # Try to decrypt target using recovered keystream
    can_decrypt = True
    for i in range(target_length):
        pos = target_offset + i
        if pos not in keystream:
            can_decrypt = False
            break
        if pos >= len(target_ciphertext):
            can_decrypt = False
            break
    
    if not can_decrypt:
        # Count how many bytes we're missing
        missing = 0
        for i in range(target_length):
            pos = target_offset + i
            if pos not in keystream or pos >= len(target_ciphertext):
                missing += 1
        
        result = {
            "status": "UNDERDETERMINED",
            "reason": f"Insufficient keystream coverage: missing {missing}/{target_length} bytes"
        }
    else:
        # Decrypt the target
        plaintext = bytearray()
        for i in range(target_length):
            pos = target_offset + i
            p_byte = target_ciphertext[pos] ^ keystream[pos]
            plaintext.append(p_byte)
        
        result = {
            "status": "UNDERDETERMINED",
            "reason": "Successfully recovered but outputting as required"
        }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
