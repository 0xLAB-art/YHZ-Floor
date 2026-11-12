c1 = bytes.fromhex("aae9adc5050d3b3697ad1ef674d3554f29d2845e27b22876a391d3de0c9208c1ce4ebe3acb2afe903f68ead160d2d88678f31bcd16c5031f5bf34b693a144166")
c2 = bytes.fromhex("cc3decb1db70327dc5f17ff466a44687824b774c32625eb2c2e4fbbcc2059b618bc038e6804a83186c28096fbf3d7c51ee365a00e44ebc6992aaf0346026e1ac")
import time
t0 = time.monotonic_ns()
ks = bytes(a ^ b for a, b in zip(c2, bytes(64)))
p1 = bytes(a ^ b for a, b in zip(c1, ks))
dt = time.monotonic_ns() - t0
print(f"OPSPAN_NS:{dt}")
print("CLAIM:" + __import__('json').dumps({"plaintext_hex": p1.hex()}))