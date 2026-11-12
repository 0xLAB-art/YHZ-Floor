import sys, time
c1_hex = 'bdd73738b8abfc8ce239f61405462372be53910c71025fe4dbfcc2780a742aea14cdf626b4b48d06827612fa3a6bcf8107d01dc59775d59dcf0a04a0dd0c84c1'
c2_hex = 'ecb057a570411809c01018eb2cef82164548794ae98e2581e58fc8fdcedc561be53fb2bb62a1abb732e313cba1902fb86d13094d2bba9d64b29d337cd0195c5f'
start = time.monotonic_ns()
c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)
p = bytes(a ^ b for a, b in zip(c1, c2))
elapsed = time.monotonic_ns() - start
sys.stdout.write(f'OPSPAN_NS:{elapsed}\n')
sys.stdout.write('CLAIM:{"plaintext2_hex":"' + p.hex() + '"}\n')
sys.stdout.flush()