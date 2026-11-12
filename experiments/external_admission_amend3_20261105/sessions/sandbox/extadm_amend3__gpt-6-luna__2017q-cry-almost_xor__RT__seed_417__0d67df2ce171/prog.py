import base64

with open('almostxor.py', 'rb') as f:
    src = base64.b64decode(f.read()).decode('ascii')
exec(src)

with open('ciphertext', 'rb') as f:
    ct = base64.b64decode(f.read()).decode('ascii').strip()

for n in range(1, 8):
    cvals = get_nums(ct, n)
    for k in range(256):
        krep = chr(k) * (len(ct) // 1 + 1)
        krep = krep[:len(ct)]
        kvals = get_vals(get_num(krep, n), n)
        ok = True
        for i in range(len(cvals)):
            m = (cvals[i] - kvals[i % len(kvals)]) & ((1 << n) - 1)
            if m >= 256:
                ok = False
                break
        if ok:
            print('n=%d k=%d' % (n, k))
            print(get_chrs(cvals, n))
