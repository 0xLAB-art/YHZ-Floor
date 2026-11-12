import sys
import json

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse known plaintexts
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Determine covered positions
    covered_positions = set()
    for kp in known_plaintexts:
        offset = kp['offset']
        length = len(bytes.fromhex(kp['data']))
        for pos in range(offset, offset + length):
            covered_positions.add(pos)
    
    # Check target coverage
    target_offset = target['offset']
    target_length = target['length']
    target_positions = set(range(target_offset, target_offset + target_length))
    
    # Count overlap
    overlap = covered_positions.intersection(target_positions)
    
    result = {
        "status": "UNDERDETERMINED",
        "reason": f"Target requires keystream at positions {target_offset}-{target_offset + target_length - 1}, but known plaintexts only reveal keystream at non-overlapping positions"
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()