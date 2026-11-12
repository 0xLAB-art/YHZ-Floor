import sys
import json
import base64
import time

def padding_oracle(forged_prev, target_block):
    query = forged_prev + target_block
    query_b64 = base64.b64encode(query).decode()
    print(json.dumps({"q": query_b64}), flush=True)
    response = json.loads(input())
    return response["pad_ok"]

def decrypt_block(target_block, prev_block):
    decrypted = bytearray(16)
    intermediate = bytearray(16)
    
    for pad_len in range(1, 17):
        forged = bytearray(16)
        
        for i in range(16 - pad_len, 16):
            forged[i] = intermediate[i] ^ pad_len
        
        found = False
        for guess in range(256):
            forged[16 - pad_len] = guess
            
            if padding_oracle(bytes(forged), target_block):
                intermediate[16 - pad_len] = guess ^ pad_len
                
                if pad_len == 1:
                    forged_test = bytearray(forged)
                    forged_test[14] ^= 1
                    if not padding_oracle(bytes(forged_test), target_block):
                        continue
                
                found = True
                break
        
        if not found:
            raise Exception(f"Failed to find byte at position {16 - pad_len}")
    
    for i in range(16):
        decrypted[i] = intermediate[i] ^ prev_block[i]
    
    return bytes(decrypted)

with open(sys.argv[1], 'r') as f:
    task = json.load(f)

ct = bytes.fromhex(task['public_input']['ct_hex'])
iv = bytes.fromhex(task['public_input']['iv_hex'])

num_blocks = len(ct) // 16
blocks = [ct[i*16:(i+1)*16] for i in range(num_blocks)]

start_time = time.monotonic_ns()

plaintext = b''
for i in range(num_blocks):
    prev = iv if i == 0 else blocks[i - 1]
    decrypted = decrypt_block(blocks[i], prev)
    plaintext += decrypted

end_time = time.monotonic_ns()

plaintext_hex = plaintext.hex()

print(f"OPSPAN_NS:{end_time - start_time}")
print(f"CLAIM:{json.dumps({'plaintext_hex': plaintext_hex})}")