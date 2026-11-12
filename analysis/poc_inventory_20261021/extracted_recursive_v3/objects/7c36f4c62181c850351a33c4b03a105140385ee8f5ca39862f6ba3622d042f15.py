import sys, json
pt_hex = "00"*64
sys.stdout.write("CLAIM:"+json.dumps({"plaintext_hex": pt_hex})+"\n")
sys.stdout.flush()