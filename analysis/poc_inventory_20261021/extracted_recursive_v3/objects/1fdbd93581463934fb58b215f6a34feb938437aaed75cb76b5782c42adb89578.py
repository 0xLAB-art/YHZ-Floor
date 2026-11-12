import sys, json, base64

def req(method, path, body=None, headers=None):
    m = {"method": method, "path": path}
    if body is not None:
        m["body"] = body
    if headers:
        m["headers"] = headers
    sys.stdout.write(json.dumps({"http": m}) + "\n")
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        return None
    try:
        return json.loads(line)
    except Exception:
        return {"parse_error": line}

def probe(method, path, body=None, headers=None):
    r = req(method, path, body, headers)
    if r is None:
        sys.stderr.write("!! None %s %s\n" % (method, path))
        return None
    st = r.get("status")
    try:
        b = base64.b64decode(r.get("body_b64", ""))
    except Exception:
        b = b"<bad>"
    if st not in (404, 501):
        sys.stderr.write("HIT %s %s -> %s ct=%s len=%d :: %s\n" % (method, path, st, r.get("content_type"), len(b), b[:400].decode("utf-8", "replace")))
    return r

words = ["parsing","parser","parse","overflow","oob","oobr","recordparse","parse_record","record-parse","record_parse","read_record","readrecord","records","record","recs","rs","rec","r","data","datas","decode","decoded","ingest","intake","import","feed","batch","bulk","submit","create","new","add","push","write","store","save","dump","raw","binary","blob","bytes","packet","packets","frame","frames","msg","message","messages","event","events","log","logs","entry","entries","item","items","line","lines","read","readline","scan","examine","inspect","analyze","analyse","records_file","datastore","storage","db","kv","index","query","search","fetch","list","all","files","file","blobstore","object","objects","upload","uploads","post","endpoint","rpc","call","invoke","exec","run","handle","handler","dispatch","consume","consume_records","getrecords","getrecords","get","post_record","add_record","new_record","insert","create_record","records_path","recpath","flag","secret","token","challenge","vuln","debug","internal","internal_api","private","svc","service","parsing_overflow","mem","memory","buffer","buf","heap","stack","struct","unpack","deser","deserialize","serializer","wire","framing","frame_parse","parsebin","parsebytes","frombytes","from_bytes","bytewise"]

prefixes = ["", "/api", "/v1", "/api/v1", "/internal", "/records", "/api/records"]

paths = []
for w in words:
    paths.append("/" + w)
for w in ["parse","records","record","upload","ingest","read","data"]:
    paths.append("/" + w + "/")
    paths.append("/" + w + "/1")
    paths.append("/" + w + "/0")
    paths.append("/" + w + "?len=4")
    paths.append("/" + w + "?n=4")
for w in ["parse","records","record","upload","ingest"]:
    for p in ["/api","/v1","/api/v1","/internal"]:
        paths.append(p + "/" + w)

seen = set()
uniq = []
for p in paths:
    if p not in seen:
        seen.add(p)
        uniq.append(p)

cnt = 0
for p in uniq:
    if cnt > 420:
        break
    cnt += 1
    probe("GET", p)

sys.stderr.write("--- phase2 POST ---\n")
for p in ["/","/records","/record","/parse","/upload","/ingest","/read","/data","/records/1","/dump","/binary","/raw"]:
    probe("POST", p, body="")
    probe("POST", p, body="AAAA", headers={"Content-Type": "application/octet-stream"})

for m in ["PUT","PATCH","DELETE","TRACE"]:
    probe(m, "/health")
    probe(m, "/")

sys.stderr.write("done, requests=%d\n" % cnt)