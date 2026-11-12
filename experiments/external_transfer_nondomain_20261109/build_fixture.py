#!/usr/bin/env python3
"""Fixture generator — the non-crypto transfer-witness task (CSAW-style audit
forensics, zero-crypto): recover the attacker's exfiltration marker from a
synthetic syslog.

Structure (mirrors the zero-reference premise owner out-of-domain):
  - 8 hosts x 6 cron intervals = 48 (host, interval) combinations, EACH with a
    planted "marker" line whose payload is a plausible flag-like token;
  - exactly ONE combination (web-03, every-17-minutes) spells the TRUE flag;
    every other combination spells an equally plausible decoy token;
  - the true combination appears in NO artifact file (hosts.cfg lists only
    legitimate 5/10/15/30/60-minute jobs; interval 17 and host web-03's
    intrusion are stated ONLY in the load-bearing premise sentence);
  - therefore the premise does not make the task easier --- it SELECTS the
    answer among artifacts-indistinguishable alternatives (the zero-reference
    structure, in a non-crypto domain).
The flag is C1-checked byte-exactly (whole stripped stdout).
"""
import hashlib
import json
import random
from pathlib import Path

NS = Path(__file__).resolve().parent
HOSTS = ["web-01", "web-02", "web-03", "web-04", "db-01", "db-02", "auth-01", "backup-01"]
INTERVALS = [5, 10, 15, 17, 30, 60]          # 17 = the attacker's interval
LEGIT_INTERVALS = [5, 10, 15, 30, 60]        # what hosts.cfg discloses
TRUE_HOST, TRUE_INTERVAL = "web-03", 17
FLAG = "flag{n0n_cr7pt0_pr3m15e_5h4r35_7h3_0wn3r}"

rng = random.Random(20261109)


def marker_token(host: str, interval: int, true: bool) -> str:
    """A plausible flag-shaped token per (host, interval); the true one is FLAG."""
    if true:
        return FLAG
    h = hashlib.sha256(f"{host}#{interval}".encode()).hexdigest()
    body = "".join(
        chr(ord("a") + int(h[i:i + 2], 16) % 26) if i % 3 else h[i]
        for i in range(0, 26, 2))
    return f"flag{{{body[:22]}}}"


def decoy_line(ts, host, prog, msg):
    return f"2026-11-08T{ts:02d}:{(ts * 7) % 60:02d}:{(ts * 13) % 60:02d}Z {host} {prog}[{rng.randint(100, 99999)}]: {msg}"


def main():
    lines = []
    # (1) the 48 planted marker lines: one per (host, interval) combination,
    #     minute-of-hour == interval (so the premise's interval is the selector),
    #     interleaved through a large noise body.
    combos = [(h, iv) for h in HOSTS for iv in INTERVALS]
    for idx, (host, iv) in enumerate(combos):
        hour = 3 + (idx % 2)                      # the window 03:00-04:59
        minute = iv                                # the minute == interval
        tok = marker_token(host, iv, host == TRUE_HOST and iv == TRUE_INTERVAL)
        lines.append((idx, f"2026-11-11T{hour:02d}:{minute:02d}:{(idx * 11) % 60:02d}Z {host} CRON[{1800 + idx}]: ({host}-job) MARKER-PAYLOAD={tok}"))
    # (2) heavy legitimate noise: ~3,900 lines of admin/daemon traffic
    progs = ["sshd", "systemd", "nginx", "postgres", "cron", "kubelet", "auditd"]
    msgs = ["session opened for user root", "connection reset by peer",
            "poll timed out", "backup checkpoint written", "health probe ok",
            "rotation completed", "auth failure count=0", "cache miss ratio 0.11"]
    for k in range(3900):
        lines.append((1000 + k, decoy_line(rng.randint(0, 23), rng.choice(HOSTS),
                                           rng.choice(progs), rng.choice(msgs))))
    lines.sort(key=lambda x: x[0])
    syslog = "\n".join(t for _, t in lines) + "\n"
    # (3) hosts.cfg: legitimate cron jobs ONLY (5/10/15/30/60) — no 17 anywhere
    cfg = ["# /etc/crontab — managed by puppet, do not edit"]
    for h in HOSTS:
        for iv in LEGIT_INTERVALS:
            cfg.append(f"{h}: cron '{iv}-min maintenance window' runs every {iv} minutes")
    cfg.append("# end of file")
    # (4) write fixtures
    (NS / "fixtures" / "tasks" / "2026x-audit-exfil").mkdir(parents=True, exist_ok=True)
    (NS / "fixtures" / "tasks" / "2026x-audit-exfil" / "syslog").write_text(syslog)
    (NS / "fixtures" / "tasks" / "2026x-audit-exfil" / "hosts.cfg").write_text("\n".join(cfg) + "\n")
    # (5) oracle
    (NS / "oracle").mkdir(exist_ok=True)
    (NS / "oracle" / "answers.json").write_text(json.dumps(
        {"answers": {"2026x-audit-exfil": FLAG}}, indent=1) + "\n")
    # (6) reference solver (stdlib-only, premise-informed) — criterion-5 receipt
    solver = '''#!/usr/bin/env python3
"""Reference solver: parse the syslog with the stated premise (host web-03,
every-17-minutes) and print the marker payload. Stdlib-only."""
import sys
p = sys.argv[1]
for line in open(p, encoding="utf-8", errors="replace"):
    if " MARKER-PAYLOAD=" in line and " web-03 " in line:
        ts = line.split(" ")[0]
        minute = int(ts.split(":")[1])
        if minute == 17:
            print(line.split("MARKER-PAYLOAD=")[1].strip())
            break
'''
    (NS / "selection").mkdir(exist_ok=True)
    (NS / "selection" / "solve_audit_exfil.py").write_text(solver)
    # (7) self-test: the solver reproduces the pin; decoys are plausible but wrong
    import subprocess, sys as s
    r = subprocess.run([s.executable, "-I", str(NS / "selection" / "solve_audit_exfil.py"),
                        str(NS / "fixtures" / "tasks" / "2026x-audit-exfil" / "syslog")],
                       capture_output=True, text=True)
    assert r.stdout.strip() == FLAG, f"reference solve mismatch: {r.stdout!r}"
    decoys = {marker_token(h, iv, False) for h in HOSTS for iv in INTERVALS
              if not (h == TRUE_HOST and iv == TRUE_INTERVAL)}
    assert FLAG not in decoys and len(decoys) == 47
    manifest = {"schema": "transfer-fixture-manifest/1", "task_id": "2026x-audit-exfil",
                "true_host": TRUE_HOST, "true_interval": TRUE_INTERVAL,
                "decoy_combinations": 47, "flag_sha256": hashlib.sha256(FLAG.encode()).hexdigest(),
                "self_test": "PASS (reference solver reproduces the pin; 47 decoys plausible and distinct)"}
    (NS / "fixtures" / "tasks" / "2026x-audit-exfil" / "manifest.json").write_text(
        json.dumps(manifest, indent=1) + "\n")
    print(json.dumps({"fixture": "2026x-audit-exfil", "syslog_bytes": len(syslog),
                      "markers": 48, "decoys": 47, "reference_solve": "MATCH",
                      "flag": FLAG[:20] + "..."}, indent=1))


if __name__ == "__main__":
    main()
