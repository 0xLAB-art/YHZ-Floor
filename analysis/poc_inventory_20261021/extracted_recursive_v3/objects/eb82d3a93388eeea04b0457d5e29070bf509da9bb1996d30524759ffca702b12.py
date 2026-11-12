import sys,time
start=time.monotonic_ns()
c1=bytes.fromhex('50ae45b190e1e29f9f115c516127ddf59a20c9cab427469aff7d17d9ded211ebec9a651d4ed6b1a51927992ed32f9ef013f01a41afd2e8442110e15793a0c128')
c2=bytes.fromhex('ef1c3d9ed84dc1d0f4efeeb783b77be8b2a4722a6b414828fa2e2af3e7c4d361a35ae7bd7de37f854de8d034cd9305f664962565995b757eb0fb47f3524374bb')
p1=bytes(a^b for a,b in zip(c1,c2))
end=time.monotonic_ns()
print(f'OPSPAN_NS:{end-start}', flush=True)
print(f'CLAIM:{{"plaintext_hex":"{p1.hex()}"}}', flush=True)