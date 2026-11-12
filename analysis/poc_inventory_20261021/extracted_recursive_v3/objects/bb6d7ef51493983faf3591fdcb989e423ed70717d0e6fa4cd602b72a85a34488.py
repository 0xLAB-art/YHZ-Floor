import time
t0 = time.monotonic_ns()
c1 = bytes.fromhex("50afa108fafaceb0a00ba0d558e655595626a328d076000592f878d5ea75edfc24e82b9dc29ed9185920a69e68760f853bf1c58426e57973e5e21957784b2c2d")
c2 = bytes.fromhex("094e2c75e0acf2fae7826537f11d69c3f1129e312360d0ff32c57f31f9f06efd5a8cd6045c71c56a7ffd9602ce5c5fcb70e8155628964c63605ce0c8797b59f7")
ks = c2
p1 = bytes(a ^ b for a, b in zip(c1, ks))
opspan = time.monotonic_ns() - t0
print(f"OPSPAN_NS:{opspan}")
print("CLAIM:" + '{"plaintext2_hex": "' + p1.hex() + '"}')