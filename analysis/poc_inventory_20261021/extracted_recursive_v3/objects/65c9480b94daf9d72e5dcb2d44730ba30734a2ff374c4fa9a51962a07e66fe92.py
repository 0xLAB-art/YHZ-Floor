from Crypto.Cipher import ChaCha20
c1 = bytes.fromhex("72531455668f62dc994658034ce714f657249f3098061e7b7638e2a5667fa70286bb7666bb3a640d51c3cb42c740e5a4cdb5973452da034e8d13d2bb6ecd89ca")
c2 = bytes.fromhex("323695e6faffe6aab6ea92bd3dd221f5a9ddbf6252113be7e0e7611d396ccdc8e696a2926f228a73cd551151e8b99fe2113c7834adb03e09a505d92c3d495220")
P1 = bytes(a ^ b for a, b in zip(c1, c2))
print("CLAIM:" + '{"plaintext2_hex": "' + P1.hex() + '"}')