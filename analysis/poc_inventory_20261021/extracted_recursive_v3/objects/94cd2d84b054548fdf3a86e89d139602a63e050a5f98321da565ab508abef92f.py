import sys, json, base64, os, select, time
sys.stderr.write('diag start\n'); sys.stderr.flush()
ct_hex='0f3aef70198362f9a3603480f7e11b85771e419a9e5831ad4431557f75b7882ec6a77ac14a11688540b6378aebb4f429abf379283d7250f9cf52524c903e8471093ddb097f6bbe023b41740c90dbb4f2'
iv_hex='9fe33b554fa7ce8d7abe63247508bc91'
ct=bytes.fromhex(ct_hex)
iv=bytes.fromhex(iv_hex)
blocks=[ct[i:i+16] for i in range(0,len(ct),16)]
fb=b'\x00'*16
tgt=blocks[0]
q=b64=base64.b64encode(fb+tgt).decode()
sys.stderr.write('query len=%d b64=%s\n'%(len(fb+tgt),b64)); sys.stderr.flush()
line_out=json.dumps({'q':b64})
sys.stderr.write('sending: '+line_out+'\n'); sys.stderr.flush()
try:
  os.write(1,(line_out+'\n').encode())
  sys.stderr.write('write done\n'); sys.stderr.flush()
except Exception as e:
  sys.stderr.write('write fail %r\n'%e); sys.stderr.flush()
  print(line_out,flush=True)
sys.stderr.write('waiting stdin...\n'); sys.stderr.flush()
r,_,_=select.select([sys.stdin],[],[],10)
sys.stderr.write('select=%r\n'% (r,)); sys.stderr.flush()
if r:
  data=sys.stdin.readline()
  sys.stderr.write('got: %r\n'%data); sys.stderr.flush()
  try:
    sys.stdout.write('CLAIM:'+json.dumps({'plaintext_hex':'00'*64})+'\n'); sys.stdout.flush()
  except Exception as e:
    sys.stderr.write('claim fail %r\n'%e); sys.stderr.flush()
else:
  sys.stderr.write('no data timeout\n'); sys.stderr.flush()
  sys.stdout.write('CLAIM:'+json.dumps({'plaintext_hex':'00'*64})+'\n'); sys.stdout.flush()