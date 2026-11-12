import sys, time, json
c1_hex='45f3f611a981d2c6b8d89e5b2e78effe71346c6f05b91d88392c12757748d21af5d25d7372e76733afeb4b898aa6716669992591bbdd18cd9d242c97a63bc99c'
c2_hex='b040918e0f603957bad4f5be16a0396831f1769d8c9f90be4d6fd8d463117b7dd2383de5d90c301e4c70d6d60d85ea9b7efe7f9d03a488865867c2fab7c116ac'
c1=bytes.fromhex(c1_hex)
c2=bytes.fromhex(c2_hex)
s=time.monotonic_ns()
p1=bytes(a^b for a,b in zip(c1,c2))
pt2_hex=p1.hex()
el=s-time.monotonic_ns()  # wait, this would be negative. I need to compute elapsed properly.