import sys
import json

def hex_to_bytes(h):
    return bytes.fromhex(h)

def bytes_to_hex(b):
    return b.hex()

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse ciphertexts
    ciphertexts = {}
    for ct in instance['ciphertexts']:
        idx = ct['message_index']
        ciphertexts[idx] = hex_to_bytes(ct['data'])
    
    # Parse known plaintexts and recover keystream
    keystream = {}
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext = hex_to_bytes(kp['data'])
        ciphertext = ciphertexts[msg_idx]
        
        # Recover keystream: K = P XOR C
        for i, p_byte in enumerate(plaintext):
            pos = offset + i
            c_byte = ciphertext[pos]
            k_byte = p_byte ^ c_byte
            keystream[pos] = k_byte
    
    # Check if we have enough keystream for the target
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Check coverage
    required_positions = set(range(target_offset, target_offset + target_length))
    available_positions = set(keystream.keys())
    
    if not required_positions.issubset(available_positions):
        missing = len(required_positions - available_positions)
        result = {
            "status": "UNDERDETERMINED",
            "reason": f"Only {len(required_positions & available_positions)} of {target_length} keystream bytes recovered; missing {missing} bytes needed for target decryption"
        }
    else:
        # Decrypt target
        target_ciphertext = ciphertexts[target_msg_idx]
        plaintext_bytes = bytearray()
        
        for i in range(target_length):
            pos = target_offset + i
            c_byte = target_ciphertext[pos]
            k_byte = keystream[pos]
            p_byte = c_byte ^ k_byte
            plaintext_bytes.append(p_byte)
        
        result = {
            "status": "UNDERDETERMINED",
            "reason": "Decrypted but verification not possible without additional context"
        }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
