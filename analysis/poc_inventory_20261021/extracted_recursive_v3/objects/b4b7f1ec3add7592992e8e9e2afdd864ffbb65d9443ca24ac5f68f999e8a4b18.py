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
    
    # Parse the instance
    ciphertexts = {ct['message_index']: hex_to_bytes(ct['data']) 
                   for ct in instance['ciphertexts']}
    
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Extract known plaintext for message 0
    known_pt = None
    known_offset = 0
    known_msg_index = 0
    
    for kp in known_plaintexts:
        if kp['message_index'] == 0:
            known_pt = hex_to_bytes(kp['data'])
            known_offset = kp['offset']
            known_msg_index = kp['message_index']
            break
    
    # Get ciphertext for message 0
    ct0 = ciphertexts[known_msg_index]
    
    # Extract the relevant portion of ciphertext corresponding to known plaintext
    ct0_segment = ct0[known_offset:known_offset + len(known_pt)]
    
    # Recover the keystream for this segment
    keystream = xor_bytes(known_pt, ct0_segment)
    
    # Get target ciphertext
    target_msg_index = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    ct_target = ciphertexts[target_msg_index]
    ct_target_segment = ct_target[target_offset:target_offset + target_length]
    
    # Decrypt target using the recovered keystream
    plaintext = xor_bytes(ct_target_segment, keystream[:len(ct_target_segment)])
    
    # Output result
    result = {
        "plaintext": bytes_to_hex(plaintext)
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()