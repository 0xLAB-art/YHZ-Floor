import sys

# hosts.cfg's schema and attacker-identification rule were not specified.
# Supply verified values from it, rather than guessing:
# python3 program.py ATTACKER_HOST CRON_INTERVAL
# Missing inputs or ambiguous matches cause a silent nonzero exit.

def main():
    if len(sys.argv) != 3:
        return 2
    attacker_host = sys.argv[1]
    try:
        attacker_interval = int(sys.argv[2])
    except ValueError:
        return 2
    if not attacker_host or not 0 <= attacker_interval <= 59:
        return 2

    wanted_minute = f'{attacker_interval:02d}'
    marker = 'MARKER-PAYLOAD='
    matches = []
    try:
        with open('syslog', 'r', encoding='utf-8') as log:
            for line in log:
                fields = line.split()
                if len(fields) < 5 or fields[1] != attacker_host:
                    continue
                timestamp = fields[0]
                if (len(timestamp) != 20 or timestamp[10] != 'T'
                        or timestamp[13] != ':' or timestamp[16] != ':'
                        or timestamp[19] != 'Z'):
                    continue
                if timestamp[14:16] != wanted_minute:
                    continue
                if not (fields[2].startswith('CRON[')
                        and fields[2].endswith(']:')):
                    continue
                tokens = [field[len(marker):] for field in fields[4:]
                          if field.startswith(marker)]
                if len(tokens) != 1 or not tokens[0]:
                    return 1
                matches.append(tokens[0])
    except (OSError, UnicodeError):
        return 1

    if len(matches) != 1:
        return 1
    sys.stdout.write(matches[0] + '\n')
    return 0

if __name__ == '__main__':
    sys.exit(main())
