import sys

host = "web-03"
minute_of_hour = 17
marker = "MARKER-PAYLOAD="

with open("syslog", "r", encoding="utf-8") as logfile:
    for line in logfile:
        fields = line.split()
        if len(fields) < 5 or fields[1] != host:
            continue
        try:
            minute = int(fields[0][14:16])
        except ValueError:
            continue
        if minute != minute_of_hour:
            continue
        for field in fields[4:]:
            if field.startswith(marker):
                token = field[len(marker):]
                if token:
                    sys.stdout.write(token + "\n")
                    sys.exit(0)

sys.exit(1)
