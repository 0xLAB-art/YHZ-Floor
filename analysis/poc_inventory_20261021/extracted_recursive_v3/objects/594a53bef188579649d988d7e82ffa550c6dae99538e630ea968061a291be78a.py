import sys
import json
import base64
import time

def padding_oracle(forged_prev, target_block):
    """Query the padding oracle."""
    query = forged_prev + target_block
    query_b64 = base64.b64encode(query).decode()
    print(json.dumps({"q": query_b64}), flush=True)
    response = json.loads(input())
    return response["pad_ok"]

def decrypt_block(target_block, prev_block):
    """Decrypt a single block using the padding oracle."""
    intermediate = bytearray(16)
    
    for pad_len in range(1, 17):
        # We need to find the byte at position 16 - pad_len
        target_pos = 16 - pad_len
        
        # Set up the forged previous block to produce the desired padding
        forged = bytearray(16)
        for i in range(target_pos + 1, 16):
            forged[i] = intermediate[i] ^ pad_len
        
        # Try all possible byte values
        found = False
        for guess in range(256):
            forged[target_pos] = guess
            
            if padding_oracle(bytes(forged), target_block):
                # Check if this is the correct byte or a false positive
                if pad_len == 1:
                    # Verify by changing another byte
                    test_forged = bytearray(forged)
                    test_forged[14] ^= 1
                    if not padding_oracle(bytes(test_forged), target_block):
                        # This is likely a false positive (padding is \x02\x02, not \x01)
                        continue
                
                intermediate[target_pos] = guess ^ pad_len
                found = True
                break
        
        if not found:
            raise Exception(f"Failed to find byte at position {target_pos}")
    
    # XOR intermediate with previous block to get plaintext
    plaintext = bytes(intermediate[i] ^ prev_block[i] for i in range(16))
    return plaintext

def main():
    start_time = time.monotonic_ns()
    
    # Read the task instance
    with open(sys.argv[1], 'r') as f:
        task = json.load(f)
    
    ct_hex = task['public_input']['ct_hex']
    iv_hex = task['public_input']['iv_hex']
    
    ct = bytes.fromhex(ct_hex)
    iv = bytes.fromhex(iv_hex)
    
    # Split ciphertext into 16-byte blocks
    blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
    
    # Decrypt each block
    plaintext_blocks = []
    prev = iv
    
    for block in blocks:
        pt_block = decrypt_block(block, prev)
        plaintext_blocks.append(pt_block)
        prev = block
    
    # Concatenate all plaintext blocks
    plaintext = b''.join(plaintext_blocks)
    
    # Remove PKCS#7 padding
    pad_len = plaintext[-1]
    if 1 <= pad_len <= 16:
        # Verify padding is valid
        if all(b == pad_len for b in plaintext[-pad_len:]):
            plaintext = plaintext[:-pad_len]
    
    end_time = time.monotonic_ns()
    
    print(f"OPSPAN_NS:{end_time - start_time}")
    print(f"CLAIM:{json.dumps({'plaintext_hex': plaintext.hex()})}")

if __name__ == '__main__':
    main()