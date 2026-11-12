import sys
c1_hex = '98df4decb63dcdc5f81f81a2c2e00a665e158cc9fd16f204f380028e7373838d8588c69978a9edede997f8c746bafa2b60bd54db007675d6a339a53a31e9f415'
c2_hex = '3a4d2338bac8b292e59222450974bd0e0f12fdecd68e41e218e98eb32f36817fce23f3035715b735f187ffefd2e0f87654ddb756f76fb478ed8fb1f2547b9917'
c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)
p1 = bytes(a ^ b for a, b in zip(c1, c2))
plain = p1.hex()
print(f'CLAIM:{{"plaintext_hex": "{plain}"}}')
sys.stdout.flush()