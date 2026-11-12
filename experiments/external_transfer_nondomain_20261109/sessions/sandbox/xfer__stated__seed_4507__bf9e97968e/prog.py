def main():
    prefix = "MARKER-PAYLOAD="
    with open("syslog", "r", encoding="utf-8") as log:
        for line in log:
            fields = line.split()
            if len(fields) < 2:
                continue
            timestamp, host = fields[0], fields[1]
            if host != "web-03" or timestamp[14:16] != "17":
                continue
            for field in fields[2:]:
                if field.startswith(prefix):
                    token = field[len(prefix):]
                    if token:
                        print(token)
                        return

if __name__ == "__main__":
    main()
