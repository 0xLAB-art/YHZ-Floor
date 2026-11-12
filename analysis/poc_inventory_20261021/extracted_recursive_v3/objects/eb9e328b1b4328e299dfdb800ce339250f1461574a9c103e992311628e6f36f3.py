import sys
c1_hex = "1bce1f828f6b87d95de5172f78c30c9cf4fa853c54a3b28cd6fc3eb2c500ccc33633ff0d2540d728b660e16c54c414186914e1c084457321897ebcfe6a6f90be"
c2_hex = "e788cbd9502e5831e88f9331d89f72f304d9d1818f7718aae2af66312f173bb128353585ea2be26e87677cbb5f4a03b4584c65148e22bc1dc299b7cac0a45d94"
c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)
p1 = bytes(a ^ b for a, b in zip(c1, c2))
print(f'CLAIM:{{"plaintext_hex": "{p1.hex()}"}}')