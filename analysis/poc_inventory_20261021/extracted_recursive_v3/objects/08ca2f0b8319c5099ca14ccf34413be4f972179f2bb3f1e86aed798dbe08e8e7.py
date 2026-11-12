import sys
import base64
import json

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def query_oracle(forged_prev, target_block):
    query = forged_prev + target_block
    # Ensure exactly 32 bytes
    assert len(query) == 32
    print(json.dumps({"q": base64.b64encode(query).decode()}), flush=True)
    line = sys.stdin.readline()
    if not line:
        sys.stderr.write("EOF on readline\n")
        sys.stderr.flush()
        raise Exception("No response from oracle (EOF)")
    sys.stderr.write(f"Got response: {line[:100]}\n")
    sys.stderr.flush()
    response = json.loads(line.strip())
    return response["pad_ok"]

def decrypt_block(prev_block, target_block):
    decrypted = bytearray(16)
    forged = bytearray(prev_block)
    
    for pad_len in range(1, 17):
        idx = 16 - pad_len
        for j in range(idx + 1, 16):
            forged[j] = decrypted[j] ^ pad_len
        
        for guess in range(256):
            forged[idx] = guess
            if query_oracle(bytes(forged), target_block):
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
    
    blocks = [ciphertext[i:i+16] for i in range(0, len(ciphertext), 16)]
    
    decrypted_blocks = []
    prev = iv
    for i, block in enumerate(blocks):
        sys.stderr.write(f"Decrypting block {i}\n")
        sys.stderr.flush()
        dec = decrypt_block(prev, block)
        decrypted_blocks.append(dec)
        prev = block
    
    plaintext = bytearray()
    prev = iv
    for i, dec in enumerate(decrypted_blocks):
        plaintext.extend(xor_bytes(dec, prev))
        prev = blocks[i]
    
    print(f"CLAIM:{json.dumps({'plaintext_hex': plaintext.hex()})}", flush=True)

if __name__ == "__main__":
    main()