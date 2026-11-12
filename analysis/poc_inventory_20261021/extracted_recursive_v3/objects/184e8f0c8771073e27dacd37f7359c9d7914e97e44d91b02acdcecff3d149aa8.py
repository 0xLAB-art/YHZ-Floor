import sys
import json
import base64
import time

def padding_oracle(forged_prev, target_block):
    """Query the padding oracle with two blocks."""
    query = forged_prev + target_block
    query_b64 = base64.b64encode(query).decode('ascii')
    print(json.dumps({"q": query_b64}), flush=True)
    response = json.loads(input())
    return response["pad_ok"]

def decrypt_block(target_block, prev_block):
    """Decrypt a single 16-byte block using padding oracle."""
    decrypted = bytearray(16)
    
    for pad_len in range(1, 17):
        # We're discovering byte at position 16 - pad_len
        target_pos = 16 - pad_len
        
        # Construct forged_prev that will produce the desired padding
        forged_prev = bytearray(16)
        
        # Set known bytes to produce correct padding
        for i in range(target_pos + 1, 16):
            forged_prev[i] = decrypted[i] ^ pad_len
        
        # Brute force the unknown byte
        found = False
        for guess in range(256):
            forged_prev[target_pos] = guess
            
            if padding_oracle(bytes(forged_prev), target_block):
                # This guess produced valid padding
                # The decrypted byte XOR guess = pad_len
                decrypted[target_pos] = guess ^ pad_len
                found = True
                break
        
        if not found:
            raise Exception(f"Failed to find byte at position {target_pos}")
    
    # XOR with actual previous block to get plaintext
    plaintext = bytes([decrypted[i] ^ prev_block[i] for i in range(16)])
    return plaintext

def main():
    start_time = time.monotonic_ns()
    
    # Read task instance
    with open(sys.argv[1], 'r') as f:
        task = json.load(f)
    
    ct_hex = task['public_input']['ct_hex']
    iv_hex = task['public_input']['iv_hex']
    
    ciphertext = bytes.fromhex(ct_hex)
    iv = bytes.fromhex(iv_hex)
    
    # Split ciphertext into 16-byte blocks
    blocks = [ciphertext[i:i+16] for i in range(0, len(ciphertext), 16)]
    num_blocks = len(blocks)
    
    # Decrypt each block
    plaintext_blocks = []
    
    for i in range(num_blocks):
        if i == 0:
            prev_block = iv
        else:
            prev_block = blocks[i-1]
        
        plaintext_block = decrypt_block(blocks[i], prev_block)
        plaintext_blocks.append(plaintext_block)
    
    # Concatenate all plaintext blocks
    plaintext = b''.join(plaintext_blocks)
    
    # Remove PKCS#7 padding
    pad_len = plaintext[-1]
    if 1 <= pad_len <= 16:
        # Verify padding is valid
        if all(plaintext[-i] == pad_len for i in range(1, pad_len + 1)):
            plaintext = plaintext[:-pad_len]
    
    end_time = time.monotonic_ns()
    
    print(f"OPSPAN_NS:{end_time - start_time}")
    print(f"CLAIM:{json.dumps({'plaintext_hex': plaintext.hex()})}")

if __name__ == '__main__':
    main()