import sys, json, base64

ct_hex = 'b7583493721c5b2ef83b60b933b6d93be553f54dd35093a225f693621880dc74754c7d907588eaaa840d0d32d5b66ed0109609a48d9298462d1078521097e1d2186b7c87a85f723d76a71f352ad92b1d'
iv_hex = '13469c46a1122932b501484eac4f8f01'

ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
block_size = 16
ct_blocks = [ct[i:i+block_size] for i in range(0, len(ct), block_size)]

def oracle_query(forged_prev: bytes, target: bytes) -> bool:
    q = forged_prev + target
    b64 = base64.b64encode(q).decode('ascii')
    print(json.dumps({'q': b64}))
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        return False
    resp = json.loads(line)
    return bool(resp.get('pad_ok', False))

# Decrypt each block
intermediates = []  # D_k(C_i) for each block
for idx, target in enumerate(ct_blocks):
    prev = iv if idx == 0 else ct_blocks[idx-1]
    known = [0]*block_size  # will hold intermediate bytes solved for positions > byte_pos
    intermediate = bytearray(block_size)
    # iterate from last byte to first
    for pos in range(block_size-1, -1, -1):
        pad_val = block_size - pos  # desired padding value
        # Build base forged_prev with known bytes set to produce pad_val
        base = bytearray(block_size)
        for j in range(pos+1, block_size):
            base[j] = known[j] ^ pad_val
        # brute force byte at pos
        found = False
        for guess in range(256):
            trial = base.copy()
            trial[pos] = guess
            if oracle_query(bytes(trial), target):
                # success: intermediate[pos] = guess xor pad_val
                intermediate[pos] = guess ^ pad_val
                known[pos] = intermediate[pos]
                found = True
                break
        if not found:
            raise RuntimeError(f'Failed to find byte at pos {pos}')
    intermediates.append(bytes(intermediate))

# Recover plaintext blocks
plain_blocks = []
for idx, inter in enumerate(intermediates):
    prev = iv if idx == 0 else ct_blocks[idx-1]
    pb = bytes(a ^ b for a, b in zip(inter, prev))
    plain_blocks.append(pb)

plaintext = b''.join(plain_blocks)
# Remove PKCS#7 padding if present
pad_len = plaintext[-1]
if 1 <= pad_len <= block_size and all(plaintext[-i] == pad_len for i in range(1, pad_len+1)):
    plaintext = plaintext[:-pad_len]

# Output as hex
result = {'plaintext_hex': plaintext.hex()}
print('CLAIM:' + json.dumps(result))
sys.stdout.flush()
"}]}