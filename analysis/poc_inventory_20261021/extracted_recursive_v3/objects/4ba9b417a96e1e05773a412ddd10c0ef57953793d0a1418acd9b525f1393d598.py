import sys
import base64
import json
import time

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def query_oracle(forged_prev, target_block):
    """Send query to padding oracle and return pad_ok boolean."""
    query = forged_prev + target_block
    print(json.dumps({"q": base64.b64encode(query).decode()}), flush=True)
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        raise Exception("No response from oracle (EOF)")
    response = json.loads(line.strip())
    return response["pad_ok"]

def decrypt_block(prev_block, target_block):
    """Recover the decryption of target_block (16 bytes) using padding oracle."""
    decrypted = bytearray(16)
    forged = bytearray(prev_block)  # we'll modify this
    
    for pad_len in range(1, 17):
        idx = 16 - pad_len
        # Set already-known bytes to produce correct padding
        for j in range(idx + 1, 16):
            forged[j] = decrypted[j] ^ pad_len
        
        # Brute force the current byte
        for guess in range(256):
            forged[idx] = guess
            if query_oracle(bytes(forged), target_block):
                # Found it: decrypted[idx] = forged[idx] ^ pad_len
                decrypted[idx] = forged[idx] ^ pad_len
                break
        else:
            raise Exception(f"Failed to find byte at position {idx}")
    
    return bytes(decrypted)

def main():
    ct_hex = "0b06f68f33d533837606b990ebb44348931a70c507ac325729d526cc06030f76783ba66d8fc6ea45be83f5c75522ece78721f394ab11018b206116208a42256f315ac7758e408b4ebd57dc225886b919"
    iv_hex = "e19b23cf069fff14b1abc581a6e297e0"
    
    ciphertext = bytes.fromhex(ct_hex)
    iv = bytes.fromhex(iv_hex)
    
    # Split into 16-byte blocks (5 blocks = 80 bytes)
    blocks = [ciphertext[i:i+16] for i in range(0, len(ciphertext), 16)]
    
    # Decrypt each block
    decrypted_blocks = []
    prev = iv
    for i, block in enumerate(blocks):
        dec = decrypt_block(prev, block)
        decrypted_blocks.append(dec)
        prev = block
    
    # Recover plaintext: P_i = Decrypt(C_i) XOR C_{i-1} (or IV)
    plaintext = bytearray()
    prev = iv
    for i, dec in enumerate(decrypted_blocks):
        plaintext.extend(xor_bytes(dec, prev))
        prev = blocks[i]
    
    # Output as hex (verifier will strip padding if present)
    print(f"CLAIM:{json.dumps({'plaintext_hex': plaintext.hex()})}", flush=True)

if __name__ == "__main__":
    main()