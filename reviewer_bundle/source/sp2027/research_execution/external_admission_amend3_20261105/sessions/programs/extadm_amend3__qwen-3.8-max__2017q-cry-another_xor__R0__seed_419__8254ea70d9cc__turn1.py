import sys

def main():
    with open('encrypted', 'rb') as f:
        data = f.read().strip()
    
    # The data is a hex string; decode it
    raw = bytes.fromhex(data.decode('ascii'))
    
    # The ciphertext appears to be XOR-encrypted with a repeating key.
    # Analyze the structure: it looks like a custom format.
    # Let's try XOR with common keys.
    
    # Try XOR with single byte keys
    for key in range(256):
        decrypted = bytes(b ^ key for b in raw)
        try:
            text = decrypted.decode('ascii')
            if text.isprintable() and ('flag' in text.lower() or 'CTF' in text):
                print(text)
                return
        except:
            pass
    
    # Try XOR with a repeating key pattern
    # Look at the data structure - it seems to have a header
    # Let's try XOR with 'key' or common CTF keys
    for key in [b'key', b'flag', b'CTF', b'password', b'secret']:
        decrypted = bytes(raw[i] ^ key[i % len(key)] for i in range(len(raw)))
        try:
            text = decrypted.decode('ascii')
            if text.isprintable():
                print(text)
                return
        except:
            pass
    
    # The data might be a custom encoding. Let's analyze the hex directly.
    # Looking at the pattern, it seems like each byte might be XORed with a position-based key
    for key_len in range(1, 20):
        # Try to find a repeating key using frequency analysis
        decrypted = bytes(raw[i] ^ (i % 256) for i in range(len(raw)))
        try:
            text = decrypted.decode('ascii')
            if text.isprintable() and ('flag' in text.lower() or 'CTF' in text):
                print(text)
                return
        except:
            pass
    
    # Most likely: XOR with a simple repeating key. Let's try the most common approach.
    # The first bytes might be a magic header
    magic = raw[:4]
    print(f"Magic: {magic.hex()}")
    
    # Try XOR with sequential bytes
    decrypted = bytes(raw[i] ^ i for i in range(len(raw)))
    try:
        text = decrypted.decode('ascii')
        if text.isprintable():
            print(text)
            return
    except:
        pass
    
    # Try XOR with reversed sequential
    decrypted = bytes(raw[i] ^ (255 - i) for i in range(len(raw)))
    try:
        text = decrypted.decode('ascii')
        if text.isprintable():
            print(text)
            return
    except:
        pass

if __name__ == '__main__':
    main()