import time, sys, json
c1_hex = "32f604b7d6cc0a35f250d1a363ba6f9230b084e7e54342433362ffc8efcfb09114dc733c7fcd723215774fc474befb51df152f3fb2785a9469cfe09fe518d66e"
c2_hex = "a64061ac392ef79110581ceb45a044a128c8df4c3ce6c2837995971919f227be839e5de04678c6756c5ad8a265b94e06f3ea64b53f60db9eb2787488aec3c9cb"
c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)
p1 = bytes(a ^ b for a, b in zip(c1, c2))
plaintext_hex = p1.hex()
start = time.monotonic_ns()
end = time.monotonic_ns()
sys.stdout.write(f"OPSPAN_NS:{end-start}\n")
sys.stdout.write(f"CLAIM:{json.dumps({'plaintext_hex': plaintext_hex})}\n")
sys.stdout.flush()