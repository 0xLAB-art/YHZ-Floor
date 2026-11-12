import time
import binascii

c1_hex = 'b594638a086380cfd1d3c3c7eb66d883de14e1bbb59012830170cd175a2cddcebd9eb842aab7727ba6721dad83389f2a34282389134c2ef3711d9e6cf6268b11'
c2_hex = '5cb5e2ee03ee6d96a9c6259c293801dd09d6562325951d81b2f0aa01bcce91ca9b34c7159be7cf934d09131a33a979604b2c453e385e426cc4df7bc5d4df1c82'

start = time.monotonic_ns()
c1 = binascii.unhexlify(c1_hex)
c2 = binascii.unhexlify(c2_hex)
# keystream = c2 (since plaintext zero)
keystream = c2
p1 = bytes(a ^ b for a, b in zip(c1, keystream))
plaintext_hex = binascii.hexlify(p1).decode('ascii')
end = time.monotonic_ns()

print(f'OPSPAN_NS:{end-start}')
print(f'CLAIM:{{"plaintext_hex":"{plaintext_hex}"}}', flush=True)