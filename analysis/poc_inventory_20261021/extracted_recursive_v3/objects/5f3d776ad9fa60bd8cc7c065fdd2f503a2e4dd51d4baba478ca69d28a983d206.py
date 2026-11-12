import sys, time

c1_hex = '13d071a251fb5c682b4de6c84433d667346b3d55b007e14ae9c218b4a06cbef8378af423acdd1b7fafaefbbe821ea80035c531bf8378049ede741d9929ddb005'
c2_hex = 'de067de64d9050d88ee64afce392a052bcd3de9ed64d438f2565a124125828185e15d3a6bb359d61bd031f6ca53a6a8457852892a2a3b00384480c3ae2c77bd8'

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)
p1 = bytes(a ^ b for a, b in zip(c1, c2))
plaintext_hex = p1.hex()

start = time.monotonic_ns()
_ = p1  # final operation
duration = int(time.monotonic_ns() - start)

print(f'OPSPAN_NS:{duration}', flush=True)
print(f'CLAIM:{{\"plaintext_hex\": "{plaintext_hex}"}}', flush=True)