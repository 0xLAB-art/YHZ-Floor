#!/usr/bin/env python3
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
