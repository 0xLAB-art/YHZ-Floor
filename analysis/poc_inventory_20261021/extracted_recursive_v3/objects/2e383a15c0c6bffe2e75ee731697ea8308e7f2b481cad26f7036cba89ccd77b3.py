import json
c1 = bytes.fromhex('c3c76ada981875386028a8f0323762d1895a61b01756f2f190f497d1d6cb092d5a9fd72bb9dbd8dd1f27938141ceb40700eda64e69e356526494c5390321750c')
c2 = bytes.fromhex('3e29afb32e6b5b9324c3506706a41b1c3b6f3ff23c784f9dbb3596763f9bf908c6473aa8edf0984a2cfc7530013b0ad55ec85be17e0d48e5bf8ea6089793c651')
p1 = bytes(a ^ b for a, b in zip(c1, c2))
print('CLAIM:' + json.dumps({'plaintext2_hex': p1.hex()}))