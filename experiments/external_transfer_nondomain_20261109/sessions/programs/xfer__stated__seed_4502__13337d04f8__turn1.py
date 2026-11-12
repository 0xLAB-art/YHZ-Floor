with open("syslog", "r", encoding="utf-8") as log:
    for line in log:
        fields = line.split()
        if len(fields) < 2:
            continue
        timestamp, host = fields[0], fields[1]
        if host != "web-03" or timestamp[14:16] != "17":
            continue
        _, marker, remainder = line.partition("MARKER-PAYLOAD=")
        if not marker:
            continue
        tokens = remainder.split()
        if tokens:
            print(tokens[0])
            break
