import sys,json,base64,time
prov=json.loads(sys.argv[1]) if len(sys.argv)>1 else {}
print('PROV '+json.dumps(prov)); sys.stdout.flush()
paths=['/','/healthz','/negotiate','/session','/tls','/api/negotiate','/api/session','/params','/param','/downgrade','/weak','/legacy','/v1/negotiate','/v1/session']
for p in paths:
    print(json.dumps({"http":{"method":"GET","path":p}})); sys.stdout.flush()
    line=sys.stdin.readline()
    print('REP '+p+' '+line.strip()); sys.stdout.flush()
print('DONE'); sys.stdout.flush()