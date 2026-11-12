import sys
c1_hex = '33579f5905440fef3967752ae8f2318bd7686fb3334b9ed86bf0b4c442f537d24f2a3fe666106a0f3d37ba5d4f193c394c1e5cbd1fd872ce4967fd2f96da0210'
c2_hex = '645c96116602a938fecbd9ac96d79ad57b80f2d68f0863a1cf2521bb3527cec87f6a93cae1d688ad78250549785c035dcc773dc58b66801cc98de57923178662'
c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)
p1 = bytes(a ^ b for a, b in zip(c1, c2))
plaintext2_hex = p1.hex()
sys.stdout.write(f'CLAIM:{{\"plaintext2_hex\":\"{plaintext2_hex}\"}}\n')
sys.stdout.flush()