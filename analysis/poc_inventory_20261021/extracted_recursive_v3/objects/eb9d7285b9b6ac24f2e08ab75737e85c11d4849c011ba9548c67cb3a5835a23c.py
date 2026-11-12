import sys, time
c1_hex = '5f5d29c45118151c15a016e2dd6fe903b5da8a8b9058b4ef55737dcc75c1e4478b883b135a3100febd8c67dd544009efd8cfce0efc56e40cd996cfb5bb04a079'
c2_hex = '59bac624cd63a320c3b2042d3b3d78d106845285d62c1c5bbe663afc69b5d9fda897e26a9946ef711b456b1f3693e3d7568badf967beb3b012a85f3273a6acd3'
c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)
start = time.monotonic_ns()
p = bytes(a ^ b for a, b in zip(c1, c2))
elapsed = time.monotonic_ns() - start
sys.stdout.write('CLAIM:{\"plaintext2_hex\":\"' + p.hex() + '\"}')
sys.stdout.write('\n')
sys.stdout.flush()
# optional opspan
sys.stdout.write('OPSPAN_NS:' + str(elapsed) + '\n')
sys.stdout.flush()