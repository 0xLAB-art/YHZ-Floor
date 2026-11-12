import sys, json, time
c1_hex = 'aaeba948c6273b97e692e8629c8a3e81bd940595d1791f2ebd9b708dd783d5a06f8e61c14afbd8c20a4fb9a67e014dec94930d757611d937840eb8e5cbf99ffd'
c2_hex = '8f9341740495804be214858e7bc69b69d9b1a07120a04486a1e7b2edc30158734e3272c8fe2bf0b52411ca3d604a5bfea3e813d459311cb6e7d75cf7864860f4'
start = time.monotonic_ns()
c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)
p1 = bytes(a ^ b for a, b in zip(c1, c2))
end = time.monotonic_ns()
print(f'OPSPAN_NS:{end-start}')
print('CLAIM:' + json.dumps({'plaintext_hex': p1.hex()}))
sys.stdout.flush()