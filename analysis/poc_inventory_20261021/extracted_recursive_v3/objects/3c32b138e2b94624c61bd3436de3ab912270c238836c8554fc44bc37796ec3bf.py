import sys, time
c1_hex = 'add7944b730609394c8176e7224aefaac3724721f3432eb02b56542d7c72348875d5ea419e04fb6ba370cff2cc31d0549cf84a4ddd32b078f0e35971b37cd3a0'
c2_hex = 'edd4674645d4ff8d11cdee397b44596c91106cbd3eb7b742b632c21eab26d4a017998e67d05620eaf8b4cedcd96ecb5f38160a94d904f178b529fa421708cf11'
start = time.monotonic_ns()
c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)
p1 = bytes(a ^ b for a, b in zip(c1, c2))
plaintext_hex = p1.hex()
elapsed = time.monotonic_ns() - start
print(f'CLAIM:{{"plaintext2_hex":"{plaintext_hex}"}}')
if elapsed:
    print(f'OPSPAN_NS:{elapsed}')
sys.stdout.flush()