import json

c1_hex = "2dd6b60a184efc1da5db10d1e542d32b478aca609d3cdb830e6fa6565f8572c2f6adacaba1fb310091eaf05bc6625f4eb47bf8d62908206af70ba2982a011755"
c2_hex = "293010e00fd4738e81aad246026637f42125259642adac03b03575b411d2083a3e59dd448bb82c02907863e371bf9dd88e784113d0f5bbebdc098538f64f2424"

b1 = bytes.fromhex(c1_hex)
b2 = bytes.fromhex(c2_hex)
p1 = bytes(a ^ b for a, b in zip(b1, b2))
plaintext_hex = p1.hex()
claim = {"plaintext_hex": plaintext_hex}
print("CLAIM:" + json.dumps(claim))