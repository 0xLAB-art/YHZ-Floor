import sys
import base64
import json
import time

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def query_oracle(forged_prev, target_block):
    """Send a padding oracle query and return True if padding is valid."""
    query = forged_prev + target_block
    print(json.dumps({"q": base64.b64encode(query).decode()}), flush=True)
    response = json.loads(sys.stdin.readline())
    return response.get("pad_ok", False)

def decrypt_block(oracle_prev, target_block):
    """Decrypt a single block using the padding oracle."""
    # We're finding D_k(target_block) byte by byte
    # D_k(target_block) XOR oracle_prev = plaintext_block
    # So D_k(target_block) = plaintext_block XOR oracle_prev
    
    decrypted = bytearray(16)  # This will hold D_k(target_block)
    forged_prev = bytearray(16)  # What we send as the previous block
    
    for byte_pos in range(15, -1, -1):
        pad_value = 16 - byte_pos
        
        # Set the bytes we already know to produce correct padding
        for j in range(byte_pos + 1, 16):
            forged_prev[j] = decrypted[j] ^ pad_value
        
        # Try all 256 values for the current byte
        found = False
        for guess in range(256):
            forged_prev[byte_pos] = guess
            if query_oracle(bytes(forged_prev), target_block):
                # Found it! The decrypted byte XOR forged_prev = pad_value
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
    
    # Split into blocks: IV + 5 ciphertext blocks (80 bytes = 5 blocks)
    blocks = [ct[i:i+block_size] for i in range(0, len(ct), block_size)]
    
    # Decrypt each block
    plaintext_blocks = []
    prev = iv
    for block in blocks:
        decrypted = decrypt_block(prev, block)
        plaintext_block = xor_bytes(decrypted, prev)
        plaintext_blocks.append(plaintext_block)
        prev = block
    
    # Combine all plaintext blocks
    full_plaintext = b''.join(plaintext_blocks)
    
    # Remove PKCS#7 padding
    pad_len = full_plaintext[-1]
    if 1 <= pad_len <= 16:
        if all(b == pad_len for b in full_plaintext[-pad_len:]):
            full_plaintext = full_plaintext[:-pad_len]
    
    end_time = time.monotonic_ns()
    print(f"OPSPAN_NS:{end_time - start_time}", flush=True)
    print(f"CLAIM:{json.dumps({'plaintext_hex': full_plaintext.hex()})}", flush=True)

if __name__ == "__main__":
    main()