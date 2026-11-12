import sys

with open("syslog", "r", encoding="utf-8") as log:
    for line in log:
        fields = line.split()
        if len(fields) < 5:
            continue
        if fields[1] != "web-03" or fields[0][14:16] != "17":
            continue
        for field in fields[2:]:
            if field.startswith("MARKER-PAYLOAD="):
                sys.stdout.write(field.split("=", 1)[1] + "\n")
                sys.exit(0)
