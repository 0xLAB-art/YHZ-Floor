import sys

# The attacker identity and hosts.cfg schema were not specified.
# Supply verified values rather than guessing:
# python3 script.py ATTACKER_HOST CRON_INTERVAL
# Missing, invalid, or ambiguous data cause a silent nonzero exit.

def main():
    if len(sys.argv) != 3:
        return 2
    attacker_host = sys.argv[1]
    try:
        cron_interval = int(sys.argv[2])
    except ValueError:
        return 2
    if not attacker_host or any(c.isspace() for c in attacker_host):
        return 2
    if not 0 <= cron_interval < 60:
        return 2

    prefix = 'MARKER-PAYLOAD='
    payload = None
    try:
        with open('syslog', 'r', encoding='utf-8') as log:
            for line in log:
                fields = line.split()
                if len(fields) < 2 or fields[1] != attacker_host:
                    continue
                timestamp = fields[0]
                if (len(timestamp) != 20 or timestamp[10] != 'T'
                        or timestamp[13] != ':' or timestamp[16] != ':'
                        or timestamp[19] != 'Z'):
                    continue
                minute_text = timestamp[14:16]
                if any(c not in '0123456789' for c in minute_text):
                    continue
                if int(minute_text) != cron_interval:
                    continue
                tokens = [field[len(prefix):] for field in fields[2:]
                          if field.startswith(prefix)]
                if payload is not None or len(tokens) != 1 or not tokens[0]:
                    return 1
                payload = tokens[0]
    except (OSError, UnicodeError):
        return 1

    if payload is None:
        return 1
    sys.stdout.write(payload + '\n')
    return 0

if __name__ == '__main__':
    sys.exit(main())
