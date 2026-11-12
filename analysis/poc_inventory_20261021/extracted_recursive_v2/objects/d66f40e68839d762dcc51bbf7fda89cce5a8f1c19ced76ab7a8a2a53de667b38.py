import sys
import json

def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

def bytes_to_hex(b):
    return b.hex()

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
    
    # Get the known plaintext and its corresponding ciphertext
    known_pt = known_plaintexts[0]
    known_plaintext_bytes = hex_to_bytes(known_pt['data'])
    known_message_index = known_pt['message_index']
    known_offset = known_pt['offset']
    
    # Get the ciphertext for the known message
    known_ciphertext = ciphertexts[known_message_index]
    known_ciphertext_segment = known_ciphertext[known_offset:known_offset + len(known_plaintext_bytes)]
    
    # Recover the keystream by XORing known plaintext with its ciphertext
    keystream = xor_bytes(known_plaintext_bytes, known_ciphertext_segment)
    
    # Get target ciphertext
    target_message_index = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ciphertext = ciphertexts[target_message_index]
    target_ciphertext_segment = target_ciphertext[target_offset:target_offset + target_length]
    
    # Decrypt target by XORing with keystream
    target_plaintext = xor_bytes(target_ciphertext_segment, keystream[:target_length])
    
    # Output result
    result = {
        "plaintext": bytes_to_hex(target_plaintext)
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
