import sys
import base64
import json
import time

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def query_oracle(forged_prev, target_block):
    query = forged_prev + target_block
    sys.stdout.write(json.dumps({"q": base64.b64encode(query).decode()}) + "\n")
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        raise Exception("No response from oracle (EOF)")
    response = json.loads(line.strip())
    return response.get("pad_ok", False)

def decrypt_block(oracle_prev, target_block):
    decrypted = bytearray(16)
    forged_prev = bytearray(16)
    
    for byte_pos in range(15, -1, -1):
        pad_value = 16 - byte_pos
        
        for j in range(byte_pos + 1, 16):
            forged_prev[j] = decrypted[j] ^ pad_value
        
        found = False
        for guess in range(256):
            forged_prev[byte_pos] = guess
            if query_oracle(bytes(forged_prev), target_block):
                decrypted[byte_pos] = forged_prev[byte_pos] ^ pad_value
                found = True
                break
        
        if not found:
            raise Exception(f"Failed to decrypt byte {byte_pos}")
    
    return bytes(decrypted)

def main():
    start_time = time.monotonic_ns()
    
    ct_hex = "f84b99a0337b3d169517ae8dc683f2b68e33fe2995bfcdab143b1f5900c095d00f8075c891c5ec05582eba97551106a3f032bc51dc24e9587f8fad71e5b5c362f3a81d21273f855dac53c52e335edae6"
    iv_hex = "d2047ce9c76bcebbb8527c5b8305e7bb"
    
    ct = bytes.fromhex(ct_hex)
    iv = bytes.fromhex(iv_hex)
    block_size = 16
    
    blocks = [ct[i:i+block_size] for i in range(0, len(ct), block_size)]
    
    plaintext_blocks = []
    prev = iv
    for block in blocks:
        decrypted = decrypt_block(prev, block)
        plaintext_block = xor_bytes(decrypted, prev)
        plaintext_blocks.append(plaintext_block)
        prev = block
    
    full_plaintext = b''.join(plaintext_blocks)
    
    pad_len = full_plaintext[-1]
    if 1 <= pad_len <= 16:
        if all(b == pad_len for b in full_plaintext[-pad_len:]):
            full_plaintext = full_plaintext[:-pad_len]
    
    end_time = time.monotonic_ns()
    sys.stdout.write(f"OPSPAN_NS:{end_time - start_time}\n")
    sys.stdout.write(f"CLAIM:{json.dumps({'plaintext_hex': full_plaintext.hex()})}\n")
    sys.stdout.flush()

if __name__ == "__main__":
    main()