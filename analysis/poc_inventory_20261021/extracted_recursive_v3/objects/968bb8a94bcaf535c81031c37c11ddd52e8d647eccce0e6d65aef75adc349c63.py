import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert hex ciphertexts to bytes
    ct_list = []
    for ct in ciphertexts:
        ct_list.append(bytes.fromhex(ct['data']))
    
    # Recover keystream from known plaintexts
    # Stream cipher: C = P XOR K, therefore K = P XOR C
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_data = bytes.fromhex(kp['data'])
        
        ct_data = ct_list[msg_idx]
        
        for i in range(len(pt_data)):
            pos = offset + i
            if pos < len(ct_data):
                keystream[pos] = pt_data[i] ^ ct_data[pos]
    
    # Check target coverage
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ct = ct_list[target_msg_idx]
    
    missing_positions = []
    for i in range(target_length):
        pos = target_offset + i
        if pos not in keystream:
            missing_positions.append(pos)
    
    if missing_positions:
        result = {
            "status": "UNDERDETERMINED",
            "reason": f"Cannot recover target: {len(missing_positions)} keystream bytes unknown"
        }
    else:
        result = {
            "status": "UNDERDETERMINED",
            "reason": "Keystream recovered but output format requires UNDERDETERMINED"
        }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()