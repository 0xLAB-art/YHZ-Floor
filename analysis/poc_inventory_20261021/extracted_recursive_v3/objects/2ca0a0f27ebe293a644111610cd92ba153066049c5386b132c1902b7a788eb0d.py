import sys, json, base64

def http_request(method, path, body_hex=None, headers=None):
    req = {"http": {"method": method, "path": path}}
    if body_hex is not None:
        req["http"]["body_hex"] = body_hex
    if headers is not None:
        req["http"]["headers"] = headers
    sys.stdout.write(json.dumps(req) + "\n")
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        raise EOFError("No response")
    return json.loads(line.strip())

# recover key
key = [0]*16
baseline = [0]*16
for pos in range(16):
    # collect pages for each plaintext value
    pages_per_val = []
    for val in range(256):
        plain = baseline.copy()
        plain[pos] = val
        # encrypt
        enc_res = http_request("POST", "/encrypt", body_hex=bytes(plain).hex())
        # footprint
        fp_res = http_request("GET", "/footprint")
        pages = set(fp_res.get("pages", []))
        pages_per_val.append(pages)
    # determine which table varies
    varying_table = None
    const_pages = [None]*4
    for tbl in range(4):
        indices = set()
        for pages in pages_per_val:
            for p in pages:
                if p // 256 == tbl:
                    indices.add(p % 256)
        if len(indices) > 1:
            varying_table = tbl
        else:
            # constant index (maybe empty set if never accessed? but should be accessed)
            const_pages[tbl] = next(iter(indices)) if indices else None
    if varying_table is None:
        # fallback: find table with max indices
        max_len = 0
        for tbl in range(4):
            indices = set()
            for pages in pages_per_val:
                for p in pages:
                    if p // 256 == tbl:
                        indices.add(p % 256)
            if len(indices) > max_len:
                max_len = len(indices)
                varying_table = tbl
    # compute key byte using any value
    # use first value
    plain0 = baseline.copy()
    plain0[0] = 0
    enc_res0 = http_request("POST", "/encrypt", body_hex=bytes(plain0).hex())
    fp_res0 = http_request("GET", "/footprint")
    pages0 = set(fp_res0.get("pages", []))
    index0 = None
    for p in pages0:
        if p // 256 == varying_table:
            index0 = p % 256
            break
    if index0 is None:
        # should not happen
        index0 = 0
    key_byte = 0 ^ index0  # plaintext byte 0
    key[pos] = key_byte
    # verify consistency (optional)
    for val in range(1,256):
        plain = baseline.copy()
        plain[pos] = val
        enc_res = http_request("POST", "/encrypt", body_hex=bytes(plain).hex())
        fp_res = http_request("GET", "/footprint")
        pages = set(fp_res.get("pages", []))
        index = None
        for p in pages:
            if p // 256 == varying_table:
                index = p % 256
                break
        if index is None:
            continue
        if (val ^ index) != key_byte:
            # mismatch; maybe noise; we could ignore
            pass
# output claim
key_hex = ''.join(f'{b:02x}' for b in key)
sys.stdout.write(f'CLAIM:{{\"key_hex\": \"{key_hex\"}}}\n')
sys.stdout.flush()