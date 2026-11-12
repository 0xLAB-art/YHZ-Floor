def main():
    prefix = "MARKER-PAYLOAD="
    with open("syslog", "r", encoding="utf-8") as log:
        for line in log:
            fields = line.split()
            if len(fields) < 5:
                continue
            if fields[1] != "web-03" or fields[0][14:16] != "17":
                continue
            for field in fields[4:]:
                if field.startswith(prefix):
                    token = field[len(prefix):]
                    if token:
                        print(token)
                        return

if __name__ == "__main__":
    main()
