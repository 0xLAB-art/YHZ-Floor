import sys, json, time

def main():
    c1_hex = "4187fb6b349ff2cd39671bf0f9df59d5a18a686682e08d2a43d6852cf155633554f9e0b747af25816d4851680427a6cb2ef9099b3ee7f736ed0fbaaeb76b62bc"
    c2_hex = "3896d8208eae0d58d7915c3b67074f983cd97456af3d73e0f04f7abab151e50d5a4d8caeea3b1eb470658c6e525b7c39719dc576c7b0c8fdf500aad03cb901a0"
    c1 = bytes.fromhex(c1_hex)
    c2 = bytes.fromhex(c2_hex)
    p1 = bytes(a ^ b for a, b in zip(c1, c2))
    plaintext2_hex = p1.hex()
    claim = {"plaintext2_hex": plaintext2_hex}
    start = time.monotonic_ns()
    end = time.monotonic_ns()
    opspan = end - start
    print(f"OPSPAN_NS:{opspan}")
    print(f"CLAIM:{json.dumps(claim)}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()