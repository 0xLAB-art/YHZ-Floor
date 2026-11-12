import sys

prefix = "MARKER-PAYLOAD="
with open("syslog", "r", encoding="utf-8") as log:
    for line in log:
        fields = line.split()
        if len(fields) < 5 or fields[1] != "web-03":
            continue
        try:
            minute = int(fields[0][14:16])
        except ValueError:
            continue
        if minute != 17:
            continue
        for field in fields[2:]:
            if field.startswith(prefix):
                token = field[len(prefix):]
                if token:
                    sys.stdout.write(token + "\n")
                    sys.exit(0)
sys.exit(1)
