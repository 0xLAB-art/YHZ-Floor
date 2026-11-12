import sys
import time

def main():
    start = time.monotonic_ns()
    c1_hex = '27280ad4c92f3377da137ac73dbe34662f5058568c5391ea6831e04f5a43818ca90e0e7a17535cfab588089ba00aa7d58d1a5817e079607d437ce7738251daee'
    c2_hex = 'e50fc8d17d6fbca3d3f6ee0d63fe435ce5824f2decf10466995798e93d2e36c25c2540b9d0dc5ad5ac8100796648b8d05dcf24685a7230bcde30eb3a7ec58791'
    c1 = bytes.fromhex(c1_hex)
    c2 = bytes.fromhex(c2_hex)
    p1 = bytes(a ^ b for a, b in zip(c1, c2))
    plaintext_hex = p1.hex()
    claim = {'plaintext_hex': plaintext_hex}
    # OPSPAN_NS line
    sys.stdout.write(f'OPSPAN_NS:{time.monotonic_ns() - start}\n')
    sys.stdout.flush()
    # CLAIM line
    sys.stdout.write(f'CLAIM:{claim}\n')
    sys.stdout.flush()

if __name__ == '__main__':
    main()