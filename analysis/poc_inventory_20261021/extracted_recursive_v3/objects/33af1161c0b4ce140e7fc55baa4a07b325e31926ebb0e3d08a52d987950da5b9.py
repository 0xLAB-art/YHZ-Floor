import sys
import json

def hex_to_bytes(h):
    return bytes.fromhex(h)

def bytes_to_hex(b):
    return b.hex()

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Find the ciphertext and known plaintext we need
    c0 = None
    c1 = None
    p0 = None
    
    for ct in ciphertexts:
        if ct['message_index'] == 0:
            c0 = hex_to_bytes(ct['data'])
        elif ct['message_index'] == target['message_index']:
            c1 = hex_to_bytes(ct['data'])
    
    for kp in known_plaintexts:
        if kp['message_index'] == 0:
            p0 = hex_to_bytes(kp['data'])
    
    # Recover keystream from message 0
    # K = C0 XOR P0
    keystream = xor_bytes(c0, p0)
    
    # Decrypt message 1 using the recovered keystream
    # P1 = C1 XOR K
    p1 = xor_bytes(c1, keystream)
    
    # Extract the target portion
    offset = target['offset']
    length = target['length']
    plaintext = p1[offset:offset + length]
    
    # Output result
    result = {
        "plaintext": bytes_to_hex(plaintext)
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()