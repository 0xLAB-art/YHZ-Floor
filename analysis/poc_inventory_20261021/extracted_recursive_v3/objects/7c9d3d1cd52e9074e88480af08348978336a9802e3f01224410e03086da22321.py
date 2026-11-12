import sys, time

c1_hex = '143eb073fa5571c322bd7bf2e31a676b7703ebedc99f513c0dffe0c18e87c98d88c9b9193c8b9f7adb6e8815fae89f725a3671444940c08e38ee8fa81d3c04ff'
c2_hex = 'f0367f5b0e1d1da498bdadc85a64d7bdbb259d75c8bf800105210206c1e30b1834dac7e5ead096ffd5342a577aa6d27302f5966ac5993470e09d89dd7e2e5daf'

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

p1 = bytes(a ^ b for a, b in zip(c1, c2))
plaintext_hex = p1.hex()

claim = f'CLAIM:{{"plaintext_hex": "{plaintext_hex}"}}'
print(claim)
sys.stdout.flush()