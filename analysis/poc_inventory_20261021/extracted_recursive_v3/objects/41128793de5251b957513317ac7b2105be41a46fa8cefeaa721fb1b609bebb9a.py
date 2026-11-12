import sys
import base64
import json
import time

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def query_oracle(forged_prev, target_block):
    query = forged_prev + target_block
    print(json.dumps({"q": base64.b64encode(query).decode()}), flush=True)
    line = sys.stdin.readline()
    if not line:
        raise Exception("EOF from oracle")
    response = json.loads(line.strip())
    return response["pad_ok"]

def decrypt_block(oracle_prev, target_block, block_size=16):
    decrypted = bytearray(block_size)
    forged_prev = bytearray(block_size)
    
    for pad_len in range(1, block_size + 1):
        pos = block_size - pad_len
        
        for k in range(pos + 1, block_size):
            forged_prev[k] = decrypted[k] ^ pad_len
        
        found = False
        for guess in range(256):
            forged_prev[pos] = guess
            if query_oracle(bytes(forged_prev), target_block):
                decrypted[pos] = guess ^ pad_len
                found = True
                break
        
        if not found:
            raise Exception(f"Failed to find byte at position {pos}")
    
    plaintext = xor_bytes(decrypted, oracle_prev)
    return bytes(plaintext)

def main():
    ct_hex = "3106b5c2cda3bfe01d4090408b8a4d758368b2ceac64eac4a0b48d431c69c02a711a506742b92652081189c2fa1398f08bf00c94c579f39f0334ca6198dd7fab7a628780bba80a6b35e4f8c0c3f09069"
    iv_hex = "5be753e59413db951b63e47f551ac98a"
    
    ct = bytes.fromhex(ct_hex)
    iv = bytes.fromhex(iv_hex)
    block_size = 16
    
    num_blocks = len(ct) // block_size
    blocks = [ct[i*block_size:(i+1)*block_size] for i in range(num_blocks)]
    
    plaintext_blocks = []
    start_ns = time.monotonic_ns()
    
    for i in range(num_blocks):
        prev = iv if i == 0 else blocks[i-1]
        target = blocks[i]
        pt_block = decrypt_block(prev, target, block_size)
        plaintext_blocks.append(pt_block)
    
    full_plaintext = b''.join(plaintext_blocks)
    
    pad_len = full_plaintext[-1]
    if 1 <= pad_len <= block_size:
        if all(b == pad_len for b in full_plaintext[-pad_len:]):
            full_plaintext = full_plaintext[:-pad_len]
    
    end_ns = time.monotonic_ns()
    
    print(f"CLAIM:{json.dumps({'plaintext_hex': full_plaintext.hex()})}", flush=True)
    print(f"OPSPAN_NS:{end_ns - start_ns}", flush=True)

if __name__ == "__main__":
    main()