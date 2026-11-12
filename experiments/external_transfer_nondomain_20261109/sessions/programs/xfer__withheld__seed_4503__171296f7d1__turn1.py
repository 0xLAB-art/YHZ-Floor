import sys

# The hosts.cfg format and attacker-identification rule were not provided.
# Supply confirmed values: python3 script.py ATTACKER_HOST CRON_INTERVAL
# Missing criteria or anything other than one matching line causes silent failure.

def main():
    if len(sys.argv) != 3:
        return 1
    attacker_host = sys.argv[1]
    try:
        cron_interval = int(sys.argv[2])
    except ValueError:
        return 1
    if not attacker_host or not 0 <= cron_interval <= 59:
        return 1

    prefix = 'MARKER-PAYLOAD='
    token = None
    try:
        with open('syslog', 'r', encoding='utf-8') as logfile:
            for line in logfile:
                fields = line.split()
                if len(fields) != 5:
                    continue
                timestamp, host, cron, job, payload = fields
                if host != attacker_host:
                    continue
                if (len(timestamp) != 20 or timestamp[10] != 'T'
                        or timestamp[13] != ':' or timestamp[16] != ':'
                        or timestamp[19] != 'Z'):
                    continue
                minute = timestamp[14:16]
                if not all('0' <= char <= '9' for char in minute):
                    continue
                if int(minute) != cron_interval:
                    continue
                if token is not None or not payload.startswith(prefix):
                    return 1
                token = payload[len(prefix):]
                if not token:
                    return 1
    except (OSError, UnicodeError):
        return 1

    if token is None:
        return 1
    sys.stdout.write(token + '\n')
    return 0

if __name__ == '__main__':
    sys.exit(main())
