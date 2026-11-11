import re

with open("ciphertext") as f:
    ct = "".join(f.read().split())

# The cipher is a byte-wise XOR with a repeated key, but with a twist:
# encr_vals = (m + k) & mask, where mask = (1<<n)-1. This is addition modulo 2^n,
# not XOR. However, the ciphertext is given as hex bytes, and the encryption
# processes bytes in chunks of n bits. Since n < 8 and the final output is bytes,
# we need to find n and the key.

# Let's analyze: the ciphertext is 32 bytes. The encryption splits into n-bit chunks.
# For the output to be bytes, 8 must be divisible by n (since get_chrs takes 8 values of n bits).
# Possible n: 1, 2, 4 (n=8 raises error).

# Actually, let's think differently. The operation is (m + k) mod 2^n. This is addition.
# But wait - if we XOR the ciphertext with the key, we might get something.
# Let's try to brute force small keys for each n.

# Actually, the key is likely a short string. Let's try all n in {1,2,4} and brute force keys.

for n in [1, 2, 4]:
    mask = (1 << n) - 1
    # The ciphertext bytes, each is the result of adding m and k mod 2^n
    # But the ciphertext is stored as bytes, so each byte = sum mod 256 effectively
    # since n < 8 and the values are < 2^n < 256.
    
    ct_nums = [ord(c) for c in ct]
    
    # Try brute force on key length 1 to 4
    for key_len in range(1, 5):
        # Brute force: key is key_len bytes
        # For each position, ct[i] = (m[i] + k[i mod key_len]) mod 2^n
        # But m is the flag, which is printable ASCII-ish.
        # Let's try all possible keys.
        
        import itertools
        chars = [chr(i) for i in range(256)]
        for key in itertools.product(range(256), repeat=key_len):
            # Decrypt: m[i] = (ct[i] - k[i mod key_len]) mod 2^n
            # But we need to check if the result is valid.
            # The issue: we don't know the exact mapping.
            pass

# Let's reconsider. The encryption:
# encr_vals(m, k, n) = (m + k) & mask
# So c = (m + k) mod 2^n
# Therefore m = (c - k) mod 2^n

# The flag likely starts with "flag{...". Let's use this.

for n in [1, 2, 4]:
    mask = (1 << n) - 1
    ct_nums = [ord(c) for c in ct]
    
    for key_len in range(1, 6):
        # Try to recover key assuming plaintext starts with "flag{"
        # m[0] = 'f' = 102, m[1] = 'l' = 108, m[2] = 'a' = 97, m[3] = 'g' = 103, m[4] = '{' = 123
        
        # k[i] = (ct[i] - m[i]) mod 2^n
        known = "flag{"
        key = []
        valid = True
        for i in range(min(len(known), len(ct_nums))):
            k_val = (ct_nums[i] - ord(known[i])) & mask
            key.append(k_val)
        
        # Check consistency: key should repeat
        if len(key) >= key_len:
            consistent = True
            for i in range(len(key)):
                if key[i] != key[i % key_len]:
                    consistent = False
                    break
            if consistent:
                # Decrypt full message
                m_vals = []
                for i in range(len(ct_nums)):
                    m_val = (ct_nums[i] - key[i % key_len]) & mask
                    m_vals.append(m_val)
                
                # Reconstruct bytes: the encryption groups 8 n-bit values into a byte
                # So we need to reverse get_chrs
                # get_chrs takes 8 values of n bits and produces 1 byte
                # So byte = sum of (val << (n*i)) for i in 0..7
                # Wait, let's re-read get_chrs
                
                # get_chrs(val_list, n):
                # x = val_list[0]
                # for i in 1..7: x <<= n; x += val_list[i]
                # So x = val[0] + val[1]<<n + val[2]<<2n + ... + val[7]<<7n
                # Then it extracts bytes from x (little-endian-ish)
                # for i in range(n): chrs.append(chr(x % 256)); x //= 256
                # chrs.reverse()
                # So it takes the low n bytes of x and reverses them.
                
                # Hmm, this is complex. Let me just reverse the whole process.
                
                # Actually, let me just simulate the encryption in reverse.
                # The encryption: m -> get_nums(m, n) -> get_vals -> encr_vals -> get_chrs
                # Let me reverse get_chrs first.
                
                # c_val_list = [c_vals[i:i+8] for i in range(0, len(c_vals), 8)]
                # return "".join([get_chrs(lst, n) for lst in c_val_list])
                
                # So each byte of ciphertext corresponds to 8 n-bit values.
                # get_chrs(lst, n) produces 1 byte from 8 n-bit values.
                # x = lst[0] + lst[1]<<n + ... + lst[7]<<7n
                # Then chrs = [x % 256, (x//256) % 256, ...] for n times, reversed.
                # So the byte = one of the low n bytes of x.
                
                # This means the ciphertext byte = x mod 256 (or one of the low bytes).
                # Since n < 8, x < 2^(8n). If n=4, x < 2^32, so x has up to 4 bytes.
                # chrs takes n bytes (n < 8), so for n=4, it takes 4 bytes of x.
                
                # Hmm, this is getting complicated. Let me just try to reverse it directly.
                
                # Actually, let me reconsider. The ciphertext is 32 bytes.
                # Each ciphertext byte = get_chrs(8 n-bit values) = one of the low n bytes of x.
                # Since n < 8 and we take n bytes, and x = sum of 8 n-bit values shifted.
                
                # For n=4: x = sum of 8 values of 4 bits, so x < 2^32.
                # chrs takes 4 bytes of x (little-endian), reversed.
                # So ciphertext byte 0 = x & 0xFF, byte 1 = (x>>8) & 0xFF, etc.
                # Wait, chrs.reverse() means the last byte extracted is first.
                # chrs = [x%256, (x//256)%256, (x//65536)%256, (x//16777216)%256] then reversed.
                # So chrs[0] = (x>>24)&0xFF, chrs[1] = (x>>16)&0xFF, etc.
                # So the ciphertext byte = (x >> (24 - i*8)) & 0xFF for i in 0..n-1.
                
                # Hmm wait, that doesn't seem right either. Let me re-read.
                
                # for i in range(n):
                #     chrs.append(chr(x % 256))
                #     x //= 256
                # chrs.reverse()
                
                # So chrs[0] = original x % 256, chrs[1] = (x//256) % 256, ...
                # After reverse: chrs[0] = (x>>(n-1)*8) & 0xFF, ..., chrs[n-1] = x & 0xFF.
                
                # So the ciphertext bytes for one group of 8 n-bit values are:
                # byte 0 = (x >> (n-1)*8) & 0xFF
                # byte 1 = (x >> (n-2)*8) & 0xFF
                # ...
                # byte n-1 = x & 0xFF
                
                # And x = sum_{j=0}^{7} lst[j] << (j*n)
                
                # So to reverse: given ciphertext bytes, we can reconstruct x.
                # x = sum_{i=0}^{n-1} ct_byte[i] << (i*8)
                # Then lst[j] = (x >> (j*n)) & mask
                
                # Then m_vals[j] = (lst[j] - k[j]) & mask
                # And then we need to reverse get_vals and get_nums.
                
                # get_vals(x, n) returns 8 values: [x & mask, (x>>n) & mask, ...] reversed.
                # So get_vals returns [val[7], val[6], ..., val[0]] where val[j] = (x >> (j*n)) & mask.
                # Wait: vals.append(x & mask); x >>= n; then vals.reverse().
                # So vals[0] = original x & mask (lowest n bits), ..., vals[7] = highest n bits.
                # After reverse: vals[0] = highest, vals[7] = lowest.
                
                # get_nums(s, n): splits s into n-bit chunks, converts to numbers.
                # to_num(s): x = sum ord(s[-1-i]) * 256^i. So it treats the string as big-endian bytes.
                # get_nums(s, n): sections = [s[i:i+n] for i in range(0, len(s), n)]
                # So it splits the string into chunks of n bytes, not n bits!
                
                # Wait, that's confusing. Let me re-read.
                # get_nums(s, n): sections = [s[i:i+n] for i in range(0, len(s), n)]
                # So if n=4, sections are chunks of 4 bytes.
                # to_num(x): treats x as big-endian bytes.
                
                # So get_nums(m, n) splits m into chunks of n bytes, converts each chunk to a number.
                # get_vals(x, n): splits x into 8 chunks of n bits.
                
                # So the encryption:
                # m_val_list = [get_vals(x, n) for x in get_nums(m, n)]
                # So for each chunk of n bytes of m, convert to a number, then split into 8 n-bit values.
                # Total: each n-byte chunk of m produces 8 n-bit values = n bytes. Consistent.
                
                # So the plaintext m is split into chunks of n bytes.
                # Each chunk is converted to a number (big-endian), then split into 8 n-bit values.
                # The key is also split similarly.
                # Then c_vals = [encr_vals(m_vals[i], k_vals[i % len(k_vals)], n)]
                # Then c_val_list = [c_vals[i:i+8] for i in range(0, len(c_vals), 8)]
                # return "".join([get_chrs(lst, n) for lst in c_val_list])
                
                # So each group of 8 n-bit values (which is n bytes) is converted to 1 byte via get_chrs.
                # Wait, that means n bytes of ciphertext values become 1 byte of output?
                # get_chrs(lst, n): lst has 8 values of n bits each = n bytes of data.
                # x = sum lst[j] << (j*n) = the number formed by the n bytes (little-endian in terms of n-bit chunks).
                # Then chrs = [x % 256, (x//256) % 256, ...] for n times, reversed.
                # So chrs = [byte_{n-1}, byte_{n-2}, ..., byte_0] where byte_i = (x >> (i*8)) & 0xFF.
                # And x = sum lst[j] << (j*n). Since lst[j] < 2^n, x < 2^(8n).
                # The n bytes of x are: byte_0 = x & 0xFF, byte_1 = (x>>8) & 0xFF, ..., byte_{n-1} = (x>>(n-1)*8) & 0xFF.
                # So chrs[0] = byte_{n-1} = (x >> (n-1)*8) & 0xFF, ..., chrs[n-1] = byte_0 = x & 0xFF.
                
                # So the output is n bytes per group of 8 n-bit values? No wait.
                # get_chrs returns n characters (one per byte of x's low n bytes).
                # And c_val_list groups c_vals into chunks of 8, so each group produces n output bytes.
                # So 8 n-bit values -> n output bytes. Consistent with n bytes of input.
                
                # So the ciphertext is n bytes per group of 8 n-bit values.
                # Total ciphertext length = (number of groups) * n.
                # The ciphertext is 32 bytes.
                # For n=4: 32/4 = 8 groups. Each group = 8 n-bit values = 32 bits = 4 bytes. Consistent.
                # For n=2: 32/2 = 16 groups. Each group = 8 n-bit values = 16 bits = 2 bytes. Consistent.
                # For n=1: 32/1 = 32 groups. Each group = 8 n-bit values = 8 bits = 1 byte. Consistent.
                
                # So to reverse:
                # 1. Split ciphertext into groups of n bytes.
                # 2. For each group, reconstruct x = sum ct_byte[i] << (i*8) for i in 0..n-1.
                #    Wait, chrs[0] = (x >> (n-1)*8) & 0xFF, so ct_byte[0] = (x >> (n-1)*8) & 0xFF.
                #    So x = sum ct_byte[i] << ((n-1-i)*8) for i in 0..n-1.
                # 3. lst[j] = (x >> (j*n)) & mask for j in 0..7.
                # 4. m_vals[j] = (lst[j] - k[j]) & mask.
                # 5. Reverse get_vals: the m_vals for one chunk are [val[7], val[6], ..., val[0]] where val[j] = (chunk_num >> (j*n)) & mask.
                #    Wait, get_vals returns vals reversed. vals[0] = chunk_num & mask (lowest), vals[7] = highest.
                #    After reverse: get_vals returns [highest, ..., lowest].
                #    So m_vals[j] = (chunk_num >> ((7-j)*n)) & mask.
                #    So chunk_num = sum m_vals[j] << ((7-j)*n).
                # 6. get_nums: chunk_num is a big-endian number of n bytes. So the n bytes are the big-endian representation.
                #    chunk_bytes = chunk_num.to_bytes(n, 'big').
                
                # Let me implement this.
                
                # Reconstruct plaintext
                num_groups = len(ct_nums) // n
                m_bytes = []
                for g in range(num_groups):
                    group = ct_nums[g*n:(g+1)*n]
                    # Reconstruct x
                    x = 0
                    for i in range(n):
                        x |= group[i] << ((n-1-i)*8)
                    # Extract lst[j]
                    lst = [(x >> (j*n)) & mask for j in range(8)]
                    # Decrypt
                    m_vals = [(lst[j] - key[j % key_len]) & mask for j in range(8)]
                    # Reverse get_vals: m_vals[j] = (chunk_num >> ((7-j)*n)) & mask
                    chunk_num = sum(m_vals[j] << ((7-j)*n) for j in range(8))
                    # Convert to bytes (big-endian, n bytes)
                    chunk_bytes = chunk_num.to_bytes(n, 'big')
                    m_bytes.extend(chunk_bytes)
                
                m_str = bytes(m_bytes).decode('latin-1')
                print(f"n={n}, key_len={key_len}, key={key}, m={m_str!r}")
