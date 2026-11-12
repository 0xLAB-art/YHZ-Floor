import json
import sys

def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

def bytes_to_hex(b):
    return b.hex()

def xor_bytes(b1, b2):
    return bytes(a ^ b for a, b in zip(b1, b2))

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Find the ciphertext and known plaintext for message_index 0
    c0_data = None
    p0_data = None
    
    for ct in ciphertexts:
        if ct['message_index'] == 0:
            c0_data = hex_to_bytes(ct['data'])
            break
    
    for kp in known_plaintexts:
        if kp['message_index'] == 0:
            p0_offset = kp['offset']
            p0_data = hex_to_bytes(kp['data'])
            break
    
    # Find the ciphertext for the target message
    c1_data = None
    for ct in ciphertexts:
        if ct['message_index'] == target['message_index']:
            c1_data = hex_to_bytes(ct['data'])
            break
    
    # This is a two-time pad attack
    # c0 = p0 XOR key
    # c1 = p1 XOR key
    # We know p0 and c0, so we can recover the key (or part of it)
    # key = p0 XOR c0
    
    # Extract the relevant portions
    start = p0_offset
    end = start + len(p0_data)
    
    # Recover the key stream
    key_stream = xor_bytes(p0_data, c0_data[start:end])
    
    # Now use the key to decrypt the target ciphertext
    target_offset = target['offset']
    target_length = target['length']
    
    c1_target = c1_data[target_offset:target_offset + target_length]
    
    # p1 = c1 XOR key
    # We need to align the key_stream with the target offset
    # key was recovered from offset p0_offset to p0_offset + len(p0_data)
    # We need key from target_offset to target_offset + target_length
    
    key_start_in_stream = target_offset - p0_offset
    key_end_in_stream = key_start_in_stream + target_length
    
    key_segment = key_stream[key_start_in_stream:key_end_in_stream]
    
    plaintext = xor_bytes(c1_target, key_segment)
    
    result = {
        "plaintext": bytes_to_hex(plaintext)
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()
