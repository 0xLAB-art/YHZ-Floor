import sys, json, base64, time
def http(method, path, body=None, body_hex=None, headers=None):
    o={"method": method, "path": path}
    if body is not None:
        o["body"]=body
    if body_hex is not None:
        o["body_hex"]=body_hex
    if headers is not None:
        o["headers"]=headers
    sys.stdout.write(json.dumps({"http": o})+"\n")
    sys.stdout.flush()
    line=sys.stdin.readline()
    if not line:
        return None
    try:
        j=json.loads(line)
    except:
        print(f"BADREPLY:{line[:500]}", file=sys.stderr)
        return None
    return j
def dec(reply):
    if reply is None:
        return "<noreply>"
    try:
        b=base64.b64decode(reply.get("body_b64",""))
    except Exception as e:
        return f"<b64err {e}>"
    try:
        return b[:4000].decode(errors='replace')
    except:
        return repr(b[:4000])
def raw(reply):
    if reply is None:
        return b""
    try:
        return base64.b64decode(reply.get("body_b64",""))
    except:
        return b""
import traceback
try:
    paths=["/","/parse","/record","/records","/api/parse","/api/record","/submit","/upload","/process","/decode","/unpack","/parse_record","/help","/api","/api/help","/docs","/openapi.json"]
    for p in paths:
        for m in ["GET"]:
            r=http(m,p)
            print(f"PROBE {m} {p} -> status={r.get('status') if r else None} ct={r.get('content_type') if r else None} body={dec(r)[:800]!r}", file=sys.stderr)
    # try POST variants on likely endpoints
    cand=["/parse","/record","/records","/submit","/upload","/","/api/parse"]
    for p in cand:
        for bd in ["hello", "AAAB", "\u0000\u0001\u0002"]:
            r=http("POST",p,body=bd,headers={"Content-Type":"application/octet-stream"})
            print(f"POST {p} body={bd!r} -> {r.get('status') if r else None} {dec(r)[:800]!r}", file=sys.stderr)
        for hx in ["00","0000","00000000","0100","00014142","040141424344","ff","ffff","ffffffff","100041424344","41424344"]:
            r=http("POST",p,body_hex=hx,headers={"Content-Type":"application/octet-stream"})
            print(f"POSTHEX {p} {hx} -> {r.get('status') if r else None} {dec(r)[:800]!r} rawhex={raw(r)[:200].hex()[:400]}", file=sys.stderr)
    # deeper: try length-prefixed fuzz on /parse and /record
    import struct
    fuzz_paths=["/parse","/record","/submit","/upload","/"]
    for p in fuzz_paths:
        for L in [0,1,2,4,8,16,32,63,64,65,127,128,255,256,512,1024,4096,65535,16777215]:
            payload=struct.pack(">I", L)+b"A"*min(L,64)
            hx=payload.hex()
            r=http("POST",p,body_hex=hx,headers={"Content-Type":"application/octet-stream"})
            d=dec(r)
            if "secret" in d.lower() or "flag" in d.lower() or (r and len(raw(r))>20 and any(c in d for c in ["00","ff"])):
                print(f"FUZZ {p} L={L} -> {r.get('status')} {d[:1000]!r}", file=sys.stderr)
            else:
                print(f"FUZZ {p} L={L} -> {r.get('status')} {d[:300]!r}", file=sys.stderr)
            # mismatch: declare large, send small
            payload2=struct.pack(">I", 1024)+b"B"*8
            r2=http("POST",p,body_hex=payload2.hex(),headers={"Content-Type":"application/octet-stream"})
            print(f"MISMATCH {p} decl1024/send8 -> {r2.get('status') if r2 else None} {dec(r2)[:500]!r}", file=sys.stderr)
            break
        break
    print("DONE-RECON", file=sys.stderr)
except Exception as e:
    print(f"EXC {e} {traceback.format_exc()[:2000]}", file=sys.stderr)
# dummy claim to get logs back
sys.stdout.write('CLAIM:{"secret_hex": "00"}\n')
sys.stdout.flush()