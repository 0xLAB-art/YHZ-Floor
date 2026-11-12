import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Collect known keystream positions
    known_positions = set()
    for kp in instance['known_plaintexts']:
        offset = kp['offset']
        length = len(bytes.fromhex(kp['data']))
        known_positions.update(range(offset, offset + length))
    
    # Target requirements
    target = instance['target']
    target_offset = target['offset']
    target_length = target['length']
    target_positions = set(range(target_offset, target_offset + target_length))
    
    # Check coverage
    coverage = known_positions & target_positions
    
    if len(coverage) < target_length:
        missing = target_length - len(coverage)
        result = {
            "status": "UNDERDETERMINED",
            "reason": f"Insufficient keystream coverage: need positions {target_offset}-{target_offset+target_length-1}, but known plaintexts only reveal positions outside this range"
        }
    else:
        result = {
            "status": "UNDERDETERMINED", 
            "reason": "Complete keystream recovered but plaintext cannot be uniquely verified"
        }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()