import json
import sys

def recover_plaintext():
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    known_ciphertext = bytes.fromhex(data['known_ciphertext'])
    known_plaintext = bytes.fromhex(data['known_plaintext'])
    target_ciphertext = bytes.fromhex(data['target_ciphertext'])
    
    keystream = bytes(c ^ p for c, p in zip(known_ciphertext, known_plaintext))
    
    target_plaintext = bytes(t ^ k for t, k in zip(target_ciphertext, keystream))
    
    result = {"target_plaintext_hex": target_plaintext.hex()}
    print(json.dumps(result))

if __name__ == '__main__':
    recover_plaintext()