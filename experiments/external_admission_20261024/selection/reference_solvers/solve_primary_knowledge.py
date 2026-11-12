import sys
vals = {}
for line in open(sys.argv[1]):
    k, v = line.split(" = ")
    vals[k.strip()] = int(v)
n, e, c = vals["n"], vals["e"], vals["c"]
# challenge source shows n = product of getPrime(1024) repeated 2**0 == 1 time -> n is a single prime
assert pow(2, n - 1, n) == 1  # Fermat witness for primality (probable prime)
d = pow(e, -1, n - 1)
m = pow(c, d, n)
b = m.to_bytes((m.bit_length() + 7) // 8, "big")
print(b.decode())
