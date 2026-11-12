#!/usr/bin/env python3
import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    r = int(data['signature_1']['r'], 16)
    s1 = int(data['signature_1']['s'], 16)
    z1 = int(data['signature_1']['z'], 16)
    s2 = int(data['signature_2']['s'], 16)
    z2 = int(data['signature_2']['z'], 16)
    
    n = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141
    
    k = ((z1 - z2) * pow(s1 - s2, -1, n)) % n
    d = ((s1 * k - z1) * pow(r, -1, n)) % n
    
    print(json.dumps({"d": f"{d:064x}", "k": f"{k:064x}"}))

if __name__ == '__main__':
    main()