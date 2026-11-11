import hashlib
import itertools
import string
import sys

TARGET = bytes.fromhex('a60458d2180258d47d7f7bef5236b33e86711ac926518ca4545ebf24cdc0b76c')
SALT = b'sha256'
SHA = hashlib.sha256


def solved(word):
    print('flag{' + word + '}')
    raise SystemExit


def hmac256(key, message):
    if len(key) > 64:
        key = SHA(key).digest()
    key = key + bytes(64 - len(key))
    inner = bytes((x ^ 0x36) for x in key)
    outer = bytes((x ^ 0x5c) for x in key)
    return SHA(outer + SHA(inner + message).digest()).digest()


def primary_extended(word):
    p = word.encode('utf-8')
    nl = bytes([10])
    zero = bytes([0])
    salts = (b'sha256', b'sha-256', b'SHA256', b'SHA-256')
    values = [p]
    for salt in salts:
        values.extend((
            p + salt, salt + p, p + b':' + salt, salt + b':' + p,
            p + b'$' + salt, salt + b'$' + p, salt + p + salt,
            p + salt + p, p + zero + salt, salt + zero + p,
            p + salt + nl, salt + p + nl, p + nl + salt
        ))
    for value in dict.fromkeys(values):
        digest = SHA(value).digest()
        if digest == TARGET:
            solved(word)
        if SHA(digest).digest() == TARGET:
            solved(word)
        if SHA(digest.hex().encode('ascii')).digest() == TARGET:
            solved(word)
    inner = SHA(p).digest()
    inner_hex = inner.hex().encode('ascii')
    for value in (inner + SALT, SALT + inner, inner_hex + SALT, SALT + inner_hex):
        if SHA(value).digest() == TARGET:
            solved(word)
    if hmac256(SALT, p) == TARGET or hmac256(p, SALT) == TARGET:
        solved(word)


def quick(word):
    p = word.encode('utf-8')
    if SHA(p + SALT).digest() == TARGET or SHA(SALT + p).digest() == TARGET:
        solved(word)


METHODS = []
method_keys = set()
for method_name in sorted(hashlib.algorithms_available):
    try:
        probe = hashlib.new(method_name)
    except (ValueError, TypeError):
        continue
    if probe.digest_size != 32:
        continue
    canonical = probe.name.lower()
    normalized = ''.join(c for c in canonical if c.isalnum())
    key = (canonical, normalized)
    if key not in method_keys:
        method_keys.add(key)
        METHODS.append((method_name, canonical, normalized))


def general_methods(word):
    p = word.encode('utf-8')
    nl = bytes([10])
    for method_name, canonical, normalized in METHODS:
        if normalized == 'sha256':
            continue
        salts = {normalized.encode('ascii'), canonical.encode('ascii')}
        for salt in salts:
            values = (
                p + salt, salt + p, p, p + b':' + salt,
                salt + b':' + p, salt + p + salt,
                p + salt + nl, salt + p + nl
            )
            for value in values:
                try:
                    digest = hashlib.new(method_name, value).digest()
                except (ValueError, TypeError):
                    break
                if digest == TARGET:
                    solved(word)


MASK32 = 0xffffffff
RL = (
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
    7, 4, 13, 1, 10, 6, 15, 3, 12, 0, 9, 5, 2, 14, 11, 8,
    3, 10, 14, 4, 9, 15, 8, 1, 2, 7, 0, 6, 13, 11, 5, 12,
    1, 9, 11, 10, 0, 8, 12, 4, 13, 3, 7, 15, 14, 5, 6, 2
)
RR = (
    5, 14, 7, 0, 9, 2, 11, 4, 13, 6, 15, 8, 1, 10, 3, 12,
    6, 11, 3, 7, 0, 13, 5, 10, 14, 15, 8, 12, 4, 9, 1, 2,
    15, 5, 1, 3, 7, 14, 6, 9, 11, 8, 12, 2, 10, 0, 4, 13,
    8, 6, 4, 1, 3, 11, 15, 0, 5, 12, 2, 13, 9, 7, 10, 14
)
SL = (
    11, 14, 15, 12, 5, 8, 7, 9, 11, 13, 14, 15, 6, 7, 9, 8,
    7, 6, 8, 13, 11, 9, 7, 15, 7, 12, 15, 9, 11, 7, 13, 12,
    11, 13, 6, 7, 14, 9, 13, 15, 14, 8, 13, 6, 5, 12, 7, 5,
    11, 12, 14, 15, 14, 15, 9, 8, 9, 14, 5, 6, 8, 6, 5, 12
)
SR = (
    8, 9, 9, 11, 13, 15, 15, 5, 7, 7, 8, 11, 14, 14, 12, 6,
    9, 13, 15, 7, 12, 8, 9, 11, 7, 7, 12, 7, 6, 15, 13, 11,
    9, 7, 15, 11, 8, 6, 6, 14, 12, 13, 5, 14, 13, 13, 7, 5,
    15, 5, 8, 11, 14, 14, 6, 14, 6, 9, 12, 9, 12, 5, 15, 8
)
KL = (0x00000000, 0x5a827999, 0x6ed9eba1, 0x8f1bbcdc)
KR = (0x50a28be6, 0x5c4dd124, 0x6d703ef3, 0x00000000)


def ripemd_function(j, x, y, z):
    if j < 16:
        return x ^ y ^ z
    if j < 32:
        return (x & y) | ((~x) & z)
    if j < 48:
        return (x | (~y)) ^ z
    return (x & z) | (y & (~z))


def rotate_left_32(value, amount):
    value &= MASK32
    return ((value << amount) | (value >> (32 - amount))) & MASK32


def ripemd256(message):
    bit_length = len(message) * 8
    padded = message + bytes([128])
    padded += bytes((55 - len(message)) % 64)
    padded += bit_length.to_bytes(8, 'little')
    state = [
        0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476,
        0x76543210, 0xfedcba98, 0x89abcdef, 0x01234567
    ]
    for offset in range(0, len(padded), 64):
        block = padded[offset:offset + 64]
        words = [int.from_bytes(block[i:i + 4], 'little') for i in range(0, 64, 4)]
        a, b, c, d = state[:4]
        aa, bb, cc, dd = state[4:]
        for j in range(64):
            t = rotate_left_32(a + ripemd_function(j, b, c, d) + words[RL[j]] + KL[j // 16], SL[j])
            a, d, c, b = d, c, b, t
            t = rotate_left_32(aa + ripemd_function(63 - j, bb, cc, dd) + words[RR[j]] + KR[j // 16], SR[j])
            aa, dd, cc, bb = dd, cc, bb, t
            if j == 15:
                a, aa = aa, a
            elif j == 31:
                b, bb = bb, b
            elif j == 47:
                c, cc = cc, c
            elif j == 63:
                d, dd = dd, d
        state = [
            (state[0] + a) & MASK32, (state[1] + b) & MASK32,
            (state[2] + c) & MASK32, (state[3] + d) & MASK32,
            (state[4] + aa) & MASK32, (state[5] + bb) & MASK32,
            (state[6] + cc) & MASK32, (state[7] + dd) & MASK32
        ]
    return b''.join(x.to_bytes(4, 'little') for x in state)


def special_methods(word):
    p = word.encode('utf-8')
    for salt in (b'ripemd256', b'ripemd-256', b'RIPEMD256'):
        for value in (p + salt, salt + p, p, p + b':' + salt, salt + b':' + p):
            if ripemd256(value) == TARGET:
                solved(word)


PHRASE_TEXT = '''example
Can you crack this?
can you crack this
canyoucrackthis
crack this
crack me
crackme
crackthis
cracked
crackedit
you cracked it
youcrackedit
i cracked it
icrackedit
hash me
hashme
hash cat
hashcat
hash browns
hashbrowns
salted hash
saltedhash
salty hash
saltyhash
salty
pepper
sha256
secure hash algorithm
securehashalgorithm
rainbow table
rainbowtable
rainbow tables
rainbowtables
john the ripper
johntheripper
open sesame
opensesame
secret password
secretpassword
super secret
supersecret
super secret password
supersecretpassword
this is a secret
thisisasecret
this is my password
thisismypassword
this is not secure
thisisnotsecure
this is a secure password
thisisasecurepassword
weak password
weakpassword
strong password
strongpassword
correct horse battery staple
correcthorsebatterystaple
trust no one
trustnoone
trustno1
let me in
letmein
congratulations
you found me
youfoundme
crypto is fun
cryptoisfun
cryptography is fun
cryptographyisfun
hashing is not encryption
hashingisnotencryption
hashes are not encryption
hashesarenotencryption
dont use md5
dontusemd5
use better passwords
usebetterpasswords
password security
passwordsecurity
hack the planet
hacktheplanet
the cake is a lie
thecakeisalie
there is no spoon
thereisnospoon
hello world
helloworld
hello friend
hellofriend
good luck
goodluck
challenge accepted
challengeaccepted
capture the flag
capturetheflag
flag
ctf
crypto
cryptography
encryption
decryption
method
algorithm
hash
salt
password
hunter2
uncrackable
crackable
crack me if you can
crackmeifyoucan'''

BASE_TEXT = '''password password1 password2 password3 password12 password123 password1234 password12345 passwords passwd pass pass1 pass12 pass123 pass1234 passw0rd p@ssword p@ssw0rd P@ssword P@ssw0rd P@ssw0rd! admin administrator admin1 admin123 root root123 guest guest1 login welcome welcome1 welcome123 letmein letmein1 changeme changeit default secret secret1 secret123 supersecret master master1 masterkey qwerty qwerty1 qwerty12 qwerty123 qwertyuiop qwertyui qwert qwertz azerty qazwsx qazwsxedc wsxedc 1qaz2wsx 1q2w3e4r q1w2e3r4 zaq12wsx zxcvbn zxcvbnm asdf asdfgh asdfghjkl asdf123 abc abc123 abcdef abcdefg abc12345 aaaaaa aaaaaaaa aaa111 test test1 test123 testing demo example sample temp temporary access system server computer internet online offline security secure insecure private public unknown whatever nothing something anything freedom forever always never nobody someone iloveyou iloveu iloveme loveyou loveme love love1 lovely lover lovers mylove amore amor miamor teamo tequiero kiss kisses hug hugs xoxo xxx sexy sex sexygirl playboy pussy fuck fuckyou fuckme fucking asshole bitch bastard shit bullshit god jesus jesus1 angel angels angel1 heaven blessed faith hope peace joy happy happiness smile smiles lucky lucky1 sunshine summer winter spring autumn fall flower flowers rose roses daisy lily jasmine violet purple yellow orange red green blue black white pink silver gold golden rainbow star stars moon sun sky cloud storm thunder lightning fire flame ice snow water earth wind dark darkness light shadow shadows dragon dragons monkey monkey1 tiger tigger lion bear pooh poohbear panda bunny rabbit puppy dog doggie kitty kitten cat horse mustang eagle falcon hawk wolf shark dolphin fish bird snake cobra spider scorpion butterfly ladybug dinosaur cookie chocolate candy sugar honey sweet sweety sweetheart pumpkin peach apple banana cherry strawberry blueberry coconut lemon mango pizza cheese coffee tequila vodka beer whiskey soccer football baseball basketball hockey softball tennis golf rugby cricket volleyball boxing racing nascar skater dance dancer music guitar piano drummer rock rockyou metal punk jazz rap eminem nirvana beatles queen prince matrix starwars star starcraft warcraft worldofwarcraft wow minecraft pokemon pikachu naruto sasuke sakura batman superman spiderman ironman hulk joker robin thor loki gandalf frodo harrypotter hogwarts twilight vampire zombie terminator predator alien avatar titanic spongebob tinkerbell barbie mickey minnie donald disney playstation xbox nintendo sega ferrari porsche mustang camaro corvette harley davidson mercedes toyota honda ford chevy bmw audi nike adidas samsung apple google yahoo facebook myspace twitter instagram youtube linux windows ubuntu debian kali android iphone hacker hacking hacked hack hackme cyber cybersec crypto crypt0 cryptic cipher code coder coding programmer developer software hardware database oracle mysql cisco network wireless wifi router firewall malware virus trojan exploit pwn pwned owned leet l33t elite noob ninja samurai warrior knight king queen prince princess princess1 princes princesita princesa beautiful beauty pretty hottie cutie babygirl babygurl baby baby1 honeybee bubbles cupcake peaches precious gorgeous awesome amazing magic miracle destiny dream dreams dreamer wish wishes family friends friend bestfriend bff home house school college university student teacher money dollar million winner champion boss bigboss killer hunter ranger cowboy rebel freedom america american mexico canada england london liverpool arsenal chelsea united yankees cowboys dolphins lakers bulls giants eagles packers steelers raiders redsox barcelona madrid juventus arsenal1 soccer1 football1 baseball1 dragon1 monkey1 shadow1 master1 michael michael1 jessica jennifer jordan jordan1 hunter1 charlie charlie1 andrew daniel robert thomas george william david richard joseph jose james john johnny jonathan joshua justin matthew anthony christopher christian alexander brandon brian kevin jason eric steven ryan nicholas jacob tyler zachary aaron adam alan alex albert benjamin bradley bryan caleb cameron carlos charles chris cody connor corey craig darren dennis derek dominic donald douglas dylan edward elijah ethan evan frank gabriel gary gregory henry isaac jack jackson jake jameson jeremy jesse joel joseph1 juan julian kyle larry logan louis lucas marc mark martin mason max miguel nathan noah oliver oscar patrick paul peter philip raymond ronald russell sam samuel scott sean shane simon timothy victor vincent walter wayne aaliyah abigail alexa alexandra alexis alice alicia allison alyssa amanda amber amelia amy ana andrea angela angelica anna anne ashley aubrey autumn ava barbara beatrice beth brittany brooke camila candace carla carmen carol caroline cassandra catherine cecilia charlotte chelsea chloe christina christine cindy claire courtney crystal daniela danielle deborah diana donna elena elizabeth ella emily emma erica erin eva evelyn faith felicity gabriela grace hailey hannah heather helen isabella jackie jacqueline jade jamie jane janet janice jenna jenny jessica1 joanna jocelyn julia juliana julie karen katherine kathleen katie kayla kelly kim kimberly kristen kristin laura lauren layla leah Leslie linda lisa lori madeline maria mariah marie marilyn marissa mary megan melanie melissa mia michelle monica morgan natalie natasha nicole olivia paige pamela patricia rachel rebecca riley rose samantha sandra sara sarah savannah shannon sharon shelby sophia stacey stephanie susan tanya taylor teresa tiffany tracy valerie vanessa veronica victoria violet whitney zoe time person year people way day man woman thing world life hand part child children eye place work week case point government company number group problem fact good new first last long great little own other old right big high different small large next early young important few public bad same able happy sad strong weak easy hard simple difficult fast slow hot cold warm cool clean dirty rich poor true false real fake best better worse worst beautiful ugly smart clever crazy funny serious kind nice evil sweet bitter fresh wild free safe dangerous brave quiet loud calm angry tired alive dead open closed start finish begin end enter exit up down left right north south east west one two three four five six seven eight nine ten zero hundred thousand million morning afternoon evening night today tomorrow yesterday monday tuesday wednesday thursday friday saturday sunday january february march april may june july august september october november december birthday holiday vacation weekend season rain sunny cloudy windy home room door window wall floor kitchen garden garage street road city town village country state island mountain valley river ocean sea beach forest desert space planet mars venus earth jupiter saturn universe galaxy animal human people mother father mom dad mommy daddy mama papa brother sister son daughter uncle aunt cousin grandma grandpa family1 friend1 school1 college1 book books story stories movie movies game games player gaming sport ball goal team teams car truck train plane boat ship phone mobile camera picture photo video television radio song songs sound art artist paint color food dinner lunch breakfast fruit vegetable bread cake milk cheese egg chicken beef bacon burger sandwich pasta rice soup salad health heart body mind brain head face hair mouth tooth arm leg foot blood doctor nurse hospital medicine name word words language english spanish french german italian russian chinese japanese data file files folder key keys lock locked unlock hidden found lost search find look see watch read write speak talk tell ask answer question challenge puzzle riddle solution solve solved winner winning success successful fail failure try again begin start finish final random common rare unique special normal strange weird magic power energy force speed level secretcode passcode pin codeword keyword username user account profile email mail message hello hi hey goodbye thanks please sorry yes no maybe okay ok cool awesome amazing wonderful fantastic perfect excellent brilliant clever genius stupid silly crazy insane madness chaos order truth lie trust believe remember forget think know learn teach create build break destroy make made use used want need like hate give take come go run walk jump fly swim drive ride play win lose help save kill live laugh cry smile dream sleep wake love peace war battle fight attack defend protect guard watch dog cat mouse rat fox owl deer goat sheep pig cow bull buffalo camel zebra giraffe gorilla ape koala otter badger beaver raccoon squirrel penguin parrot phoenix unicorn monster demon ghost spirit witch wizard pirate robot ninja turtle sonic mario luigi zelda link metroid doom quake halo portal bioshock fallout skyrim diablo runescape fortnite valorant counterstrike steam github git python java javascript ruby perl php html css sql binary hexadecimal decimal algorithm1 sha md5 sha1 sha224 sha384 sha512 ripemd ripemd256 blake keccak salted peppered hashbrown hashbrowns cracker cracking cracked rainbowtable crackstation johntheripper cyberpunk cyberspace infosec capturetheflag flag1 ctf1 easyctf picoctf hacker1 hacking1 password! password@123 Password Password1 Password123 P@ssword123 Welcome Welcome1 Admin Admin123 Qwerty Qwerty123 Secret Secret123 dragon123 monkey123 football123 baseball123 soccer123 princess123 sunshine123 hunter2 hunter123 trustno1 letmein123 iloveyou1 rockyou1 abc123456 123abc 123qwe qwe123 654321 987654321 112233 445566 121212 131313 696969 777777 888888 999999 000000 111111 222222 333333 444444 555555 666666 123123 321321 123321 102030 159753 147258 2580 007 420 69 666 777 911 2000 2001 2002 2003 2004 2005 2006 2007 2008 2009 2010 2011 2012 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022 2023 2024 2025 2026 hola gracias adios amigo amigos amiga familia dios estrella corazon mariposa bonita chiquita felicidad libertad siempre campeon futbol besos gatito perrito cielo vida querido querida carino brasil portugal argentina colombia espana italiano roma paris france germany deutschland london tokyo china india africa aussie australia aloha hawaii homlesspa baseball1 computer1 internet1 killer1 pepper ginger maggie biteme access austin dallas ranger hockey george michelle pepper1 amanda summer1 ashley nicole buster soccer1 harley batman1 andrew1 cheese joshua1 matrix1 taylor1 thunder1 cookie1 junior roberto daniela lauren1 yellow1 softball1 joseph1 sweety1 vanessa1 danielle1 melissa1 tigger1 chocolate1 butterfly1 lovely1 friends1 babygirl1 nicole1'''

CORE_TEXT = '''password secret super secure security hash salt salty pepper crypto cipher code flag ctf crack cracked hacker hacking cyber admin root access login welcome trust love ilove you me my your hello world friend family baby girl boy man woman king queen prince princess angel devil dragon monkey tiger lion bear wolf eagle shark spider snake horse mustang shadow master hunter ranger killer ninja samurai warrior knight cowboy rebel freedom forever sunshine summer winter spring flower rose star moon sun sky storm thunder fire flame ice snow water earth dark light black white red green blue purple pink silver gold rainbow magic dream destiny lucky happy smile sweet honey cookie chocolate candy coffee soccer football baseball basketball hockey tennis music rock metal guitar piano dance game gamer player minecraft pokemon naruto batman superman spiderman starwars matrix computer internet linux windows ubuntu android apple google python java programmer developer network wireless server database money winner champion boss big awesome amazing secretcode passcode keyword open sesame correct horse battery staple trustno letmein qwerty abc test example challenge puzzle answer solution hashcat rainbowtable hashbrown encryption decryption algorithm sha sha256 john ripper crackstation capture flag weak strong safe danger pirate robot zombie vampire unicorn phoenix home school college city country america london liverpool chelsea freedom family friends beautiful pretty lovely crazy funny cool hot cold fast furious wild free good bad best one two three four seven zero'''

phrases = []
for line in PHRASE_TEXT.splitlines():
    line = line.strip()
    if not line:
        continue
    compact = ''.join(c for c in line if c.isalnum())
    phrases.extend((
        line, line.lower(), line.upper(), line.title(), compact,
        compact.lower(), line.replace(' ', '_'), line.replace(' ', '-'),
        line.rstrip('?'), line.lower().rstrip('?')
    ))

bases = list(dict.fromkeys(BASE_TEXT.split()))
seen = set()
candidates = []
for word in phrases + bases:
    if word and word not in seen:
        seen.add(word)
        candidates.append(word)

for candidate in candidates:
    primary_extended(candidate)

for candidate in candidates:
    general_methods(candidate)

rows = (
    '1234567890', '0987654321', 'qwertyuiop', 'poiuytrewq',
    'asdfghjkl', 'lkjhgfdsa', 'zxcvbnm', 'mnbvcxz',
    'qazwsxedc', 'plokmijn', '1qaz2wsx3edc', 'zaq12wsx',
    'abcdefghijklmnopqrstuvwxyz', 'zyxwvutsrqponmlkjihgfedcba'
)
for row in rows:
    quick(row)
    quick(row.upper())
    for length in range(3, min(10, len(row)) + 1):
        for start in range(len(row) - length + 1):
            part = row[start:start + length]
            quick(part)
            quick(part.upper())
            if len(part) <= 5:
                quick(part + part)
for char in string.ascii_letters + string.digits:
    for count in range(1, 17):
        quick(char * count)
for a, b in (('a', 'b'), ('x', 'o'), ('1', '2'), ('0', '1'), ('q', 'w'), ('z', 'x')):
    for count in range(2, 9):
        quick((a + b) * count)

common_suffix_text = '''1 2 3 4 5 6 7 8 9 0 01 02 07 10 11 12 13 21 22 23 42 69 77 88 99 100 101 111 123 1234 12345 123456 321 3210 666 777 999 000 0000 007 420 911 1122 1212 1313 6969 7777 8888 9999 ! !! !!! @ @@ # $ % & * ? . _ - !1 !12 !123 1! 12! 123! @1 @123 #1 #123 01! 123@ 123# 123$ abc qwerty asdf love xoxo 1980 1981 1982 1983 1984 1985 1986 1987 1988 1989 1990 1991 1992 1993 1994 1995 1996 1997 1998 1999 2000 2001 2002 2003 2004 2005 2006 2007 2008 2009 2010 2011 2012 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022 2023 2024 2025 2026'''
suffixes = common_suffix_text.split()
suffixes.extend(str(n) for n in range(0, 101))
suffixes.extend(str(n).zfill(2) for n in range(0, 100))
suffixes.extend(str(n).zfill(3) for n in range(0, 100))
suffixes = list(dict.fromkeys(suffixes))
prefixes = ('1', '12', '123', '!', '@', '#', '$', 'my', 'the', 'i', 'x', 'xx')
mutation_bases = [w for w in bases if w.isalpha() and 2 <= len(w) <= 20]


def ordinary_forms(word):
    return list(dict.fromkeys((
        word, word.lower(), word.capitalize(), word.upper(), word[::-1],
        word.lower()[::-1], word.capitalize()[::-1]
    )))


for word in mutation_bases:
    for form in ordinary_forms(word):
        for suffix in suffixes:
            quick(form + suffix)
        for prefix in prefixes:
            quick(prefix + form)

leet_schemes = (
    (('a', '@'), ('e', '3'), ('i', '1'), ('o', '0'), ('s', '5'), ('t', '7'), ('l', '1'), ('g', '9')),
    (('a', '4'), ('e', '3'), ('i', '!'), ('o', '0'), ('s', '$'), ('t', '7'), ('b', '8'), ('g', '9'))
)
leet_suffixes = ('', '1', '12', '123', '1234', '!', '!!', '1!', '123!', '007', '69', '99', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025')
for word in mutation_bases:
    lower = word.lower()
    leet_forms = set()
    for scheme in leet_schemes:
        present = [(a, b) for a, b in scheme if a in lower][:7]
        for mask in range(1, 1 << len(present)):
            transformed = lower
            for bit, (old, new) in enumerate(present):
                if mask & (1 << bit):
                    transformed = transformed.replace(old, new)
            leet_forms.add(transformed)
    for form in leet_forms:
        for suffix in leet_suffixes:
            quick(form + suffix)
        quick(form.capitalize())

core = list(dict.fromkeys(CORE_TEXT.split()))
for first in core:
    for second in core:
        quick(first + second)
        quick(first + '_' + second)
        quick(first + '-' + second)
        quick(first + '.' + second)
        quick(first + ' ' + second)
        quick(first + second.capitalize())
        quick(first.capitalize() + second.capitalize())

small_core = core[:45]
for first, second, third in itertools.product(small_core, repeat=3):
    quick(first + second + third)

for year in range(1950, 2031):
    ys = str(year)
    yy = ys[2:]
    for month in range(1, 13):
        for day in range(1, 32):
            mm = str(month).zfill(2)
            dd = str(day).zfill(2)
            for date in (
                dd + mm + ys, mm + dd + ys, ys + mm + dd,
                dd + mm + yy, mm + dd + yy,
                dd + '-' + mm + '-' + ys, mm + '-' + dd + '-' + ys,
                dd + '/' + mm + '/' + ys, mm + '/' + dd + '/' + ys
            ):
                quick(date)

for candidate in candidates:
    special_methods(candidate)

for word in mutation_bases:
    capital = word.capitalize()
    for number in range(101, 1000):
        suffix = str(number)
        quick(word + suffix)
        quick(capital + suffix)

CHUNK_TEXT = '''a e i o u y ba be bi bo bu ca ce ci co cu da de di do du fa fe fi fo fu ga ge gi go gu ha he hi ho hu ja je ji jo ju ka ke ki ko ku la le li lo lu ma me mi mo mu na ne ni no nu pa pe pi po pu ra re ri ro ru sa se si so su ta te ti to tu va ve vi vo vu wa we wi wo ya ye yo za ze al an ar as at en er es et in ing ion is it ly or re un ant ent ous ful less ness ment able ible tion sion con com dis ex pre pro sub super trans inter cyber crypt hash pass word secret love star sun moon fire ice dark light black white blue red green gold silver rain bow dream happy lucky sweet master shadow dragon tiger angel devil magic power king queen man girl boy dog cat bear wolf fox hawk rock sky sea land home free win max neo alpha beta omega ultra mega mini'''
chunks = list(dict.fromkeys(CHUNK_TEXT.split()))
for first in chunks:
    for second in chunks:
        quick(first + second)
for first, second, third in itertools.product(chunks[:90], repeat=3):
    quick(first + second + third)

for length in range(1, 8):
    for chars in itertools.product(string.digits, repeat=length):
        quick(''.join(chars))

for length in range(1, 6):
    for chars in itertools.product(string.ascii_lowercase, repeat=length):
        quick(''.join(chars))

lower_alnum = string.ascii_lowercase + string.digits
for length in range(1, 5):
    for chars in itertools.product(lower_alnum, repeat=length):
        quick(''.join(chars))

vowels = 'aeiouy'
consonants = 'bcdfghjklmnpqrstvwxz'
for pattern in ('cvcvcv', 'vcvcvc'):
    pools = [consonants if kind == 'c' else vowels for kind in pattern]
    for chars in itertools.product(*pools):
        quick(''.join(chars))

frequent_letters = 'etaoinshrdlu'
for chars in itertools.product(frequent_letters, repeat=6):
    quick(''.join(chars))

fallback = string.ascii_lowercase + string.digits + string.ascii_uppercase + '_-!@#$%^&*().,?+= {}[];:/' + chr(92) + chr(39)
fallback = ''.join(dict.fromkeys(fallback))
for length in itertools.count(1):
    for chars in itertools.product(fallback, repeat=length):
        quick(''.join(chars))
