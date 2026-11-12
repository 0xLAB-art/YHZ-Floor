import sys

# Usage: python3 solution.py ATTACKER_HOST CRON_MINUTE
# Supply verified values: neither the attacker identity nor the hosts.cfg
# schema was specified, so this program does not guess them.
# Missing inputs, malformed matches, and ambiguity cause a silent nonzero exit.

def main():
    if len(sys.argv) != 3:
        return 2
    attacker_host = sys.argv[1]
    try:
        cron_minute = int(sys.argv[2])
    except ValueError:
        return 2
    if not attacker_host or any(c.isspace() for c in attacker_host):
        return 2
    if not 0 <= cron_minute <= 59:
        return 2

    wanted_minute = f'{cron_minute:02d}'
    marker = 'MARKER-PAYLOAD='
    selected = None
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
                    return 1
                if timestamp[14:16] != wanted_minute:
                    continue
                tokens = [field[len(marker):] for field in fields[2:]
                          if field.startswith(marker)]
                if len(tokens) != 1 or not tokens[0] or selected is not None:
                    return 1
                selected = tokens[0]
    except (OSError, UnicodeError):
        return 1

    if selected is None:
        return 1
    sys.stdout.write(selected + '\n')
    return 0

if __name__ == '__main__':
    sys.exit(main())
