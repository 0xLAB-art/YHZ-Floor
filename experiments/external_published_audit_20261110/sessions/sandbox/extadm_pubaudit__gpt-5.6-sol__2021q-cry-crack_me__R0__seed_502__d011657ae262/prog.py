import hashlib
import itertools
import re
import string
import struct
import sys

with open('README.md', 'r', encoding='utf-8') as fh:
    readme = fh.read()
hashes = re.findall(r'[0-9A-Fa-f]{64}', readme)
target = bytes.fromhex(hashes[0] if hashes else 'a60458d2180258d47d7f7bef5236b33e86711ac926518ca4545ebf24cdc0b76c')

MASK = 0xffffffff

def rol(x, n):
    return ((x << n) | (x >> (32 - n))) & MASK

def ripemd256(data):
    rl = (
        0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,
        7,4,13,1,10,6,15,3,12,0,9,5,2,14,11,8,
        3,10,14,4,9,15,8,1,2,7,0,6,13,11,5,12,
        1,9,11,10,0,8,12,4,13,3,7,15,14,5,6,2
    )
    rr = (
        5,14,7,0,9,2,11,4,13,6,15,8,1,10,3,12,
        6,11,3,7,0,13,5,10,14,15,8,12,4,9,1,2,
        15,5,1,3,7,14,6,9,11,8,12,2,10,0,4,13,
        8,6,4,1,3,11,15,0,5,12,2,13,9,7,10,14
    )
    sl = (
        11,14,15,12,5,8,7,9,11,13,14,15,6,7,9,8,
        7,6,8,13,11,9,7,15,7,12,15,9,11,7,13,12,
        11,13,6,7,14,9,13,15,14,8,13,6,5,12,7,5,
        11,12,14,15,14,15,9,8,9,14,5,6,8,6,5,12
    )
    sr = (
        8,9,9,11,13,15,15,5,7,7,8,11,14,14,12,6,
        9,13,15,7,12,8,9,11,7,7,12,7,6,15,13,11,
        9,7,15,11,8,6,6,14,12,13,5,14,13,13,7,5,
        15,5,8,11,14,14,6,14,6,9,12,9,12,5,15,8
    )
    kl = (0x00000000, 0x5a827999, 0x6ed9eba1, 0x8f1bbcdc)
    kr = (0x50a28be6, 0x5c4dd124, 0x6d703ef3, 0x00000000)

    def f(q, x, y, z):
        if q == 0:
            return (x ^ y ^ z) & MASK
        if q == 1:
            return ((x & y) | ((~x) & z)) & MASK
        if q == 2:
            return ((x | (~y)) ^ z) & MASK
        return ((x & z) | (y & (~z))) & MASK

    msg = bytearray(data)
    bit_length = len(msg) * 8
    msg.append(0x80)
    while len(msg) % 64 != 56:
        msg.append(0)
    msg.extend(struct.pack('<Q', bit_length))
    h = [0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476,
         0x76543210, 0xfedcba98, 0x89abcdef, 0x01234567]
    for off in range(0, len(msg), 64):
        x = struct.unpack('<16I', msg[off:off + 64])
        a, b, c, d = h[:4]
        aa, bb, cc, dd = h[4:]
        for j in range(64):
            q = j // 16
            t = rol((a + f(q, b, c, d) + x[rl[j]] + kl[q]) & MASK, sl[j])
            a, d, c, b = d, c, b, t
            t = rol((aa + f(3 - q, bb, cc, dd) + x[rr[j]] + kr[q]) & MASK, sr[j])
            aa, dd, cc, bb = dd, cc, bb, t
            if j == 15:
                a, aa = aa, a
            elif j == 31:
                b, bb = bb, b
            elif j == 47:
                c, cc = cc, c
            elif j == 63:
                d, dd = dd, d
        h = [
            (h[0] + a) & MASK, (h[1] + b) & MASK,
            (h[2] + c) & MASK, (h[3] + d) & MASK,
            (h[4] + aa) & MASK, (h[5] + bb) & MASK,
            (h[6] + cc) & MASK, (h[7] + dd) & MASK
        ]
    return struct.pack('<8I', *h)

methods = []
method_keys = set()

def register_method(salt, fn, slow=False):
    try:
        probe = fn(b'')
    except (ValueError, TypeError):
        return
    if len(probe) != 32:
        return
    salt_bytes = salt.encode('ascii')
    key = (salt_bytes, probe)
    if key not in method_keys:
        method_keys.add(key)
        methods.append((salt_bytes, fn, slow))

register_method('sha256', lambda d: hashlib.sha256(d).digest())
register_method('sha3256', lambda d: hashlib.sha3_256(d).digest())
register_method('blake2s', lambda d: hashlib.blake2s(d).digest())
register_method('blake2s256', lambda d: hashlib.blake2s(d).digest())
register_method('blake2b256', lambda d: hashlib.blake2b(d, digest_size=32).digest())
register_method('shake256', lambda d: hashlib.shake_256(d).digest(32))

for algorithm in sorted(hashlib.algorithms_available):
    normalized = re.sub(r'[^a-z0-9]', '', algorithm.lower())
    fn = lambda d, a=algorithm: hashlib.new(a, d).digest()
    register_method(normalized, fn)

if ripemd256(b'').hex() == '02ba4c4e5f8ecd1877fc52d64d30e37a2d9774fb1e5d026380ae0168e3c5522d':
    register_method('ripemd256', ripemd256, True)

SHA_SALT = b'sha256'

def win(candidate):
    print('flag{' + candidate + '}')
    raise SystemExit(0)

def check_primary(candidate):
    p = candidate.encode('utf-8')
    if hashlib.sha256(p + SHA_SALT).digest() == target:
        win(candidate)
    if hashlib.sha256(SHA_SALT + p).digest() == target:
        win(candidate)

def check_direct_methods(candidate, include_slow=False):
    p = candidate.encode('utf-8')
    for salt, fn, slow in methods:
        if slow and not include_slow:
            continue
        if fn(p + salt) == target or fn(salt + p) == target:
            win(candidate)

def hmac_sha256(key, message):
    if len(key) > 64:
        key = hashlib.sha256(key).digest()
    key += bytes(64 - len(key))
    outer = bytes(x ^ 0x5c for x in key)
    inner = bytes(x ^ 0x36 for x in key)
    return hashlib.sha256(outer + hashlib.sha256(inner + message).digest()).digest()

extended_seen = set()

def check_extended(candidate):
    if candidate in extended_seen:
        return
    extended_seen.add(candidate)
    p = candidate.encode('utf-8')
    separators = (b'', b':', b'$', b'-', b'_', b' ', b'|')
    nl = bytes((10,))
    for salt, fn, slow in methods:
        if fn(p) == target:
            win(candidate)
        use_separators = (b'',) if slow else separators
        for sep in use_separators:
            if fn(p + sep + salt) == target or fn(salt + sep + p) == target:
                win(candidate)
        if not slow:
            if fn(p + salt + nl) == target or fn(salt + p + nl) == target:
                win(candidate)
    for salt in (b'sha256', b'SHA256', b'sha-256', b'SHA-256', b'Sha256'):
        for sep in separators:
            if hashlib.sha256(p + sep + salt).digest() == target:
                win(candidate)
            if hashlib.sha256(salt + sep + p).digest() == target:
                win(candidate)
    if hmac_sha256(SHA_SALT, p) == target or hmac_sha256(p, SHA_SALT) == target:
        win(candidate)
    inner_raw = hashlib.sha256(p).digest()
    inner_hex = hashlib.sha256(p).hexdigest().encode('ascii')
    for inner in (inner_raw, inner_hex):
        if hashlib.sha256(inner + SHA_SALT).digest() == target:
            win(candidate)
        if hashlib.sha256(SHA_SALT + inner).digest() == target:
            win(candidate)
    for data in (p + SHA_SALT, SHA_SALT + p):
        if hashlib.sha256(hashlib.sha256(data).digest()).digest() == target:
            win(candidate)
        if hashlib.sha256(hashlib.sha256(data).hexdigest().encode('ascii')).digest() == target:
            win(candidate)

root_blob = '''
password password1 password12 password123 password1234 pass passwd passcode letmein letmeinnow welcome welcome1 admin administrator root guest login secret supersecret qwerty qwerty1 qwerty123 qwertyuiop asdf asdfgh asdfghjkl zxcvbn zxcvbnm qazwsx wsxzaq 1qaz2wsx 1q2w3e4r q1w2e3r4 q1w2e3r4t5 zaq12wsx 1234qwer
1234 12345 123456 1234567 12345678 123456789 1234567890 000000 111111 222222 333333 444444 555555 666666 777777 888888 999999 121212 123123 123321 112233 131313 159753 654321 696969 987654 987654321 8675309 232323 123654 12344321
abc abc123 test testing example sample demo changeme default master trustno1 access freedom whatever forever iloveyou iloveu iloveme loveme loveyou love mylove lovely lover lovers friends family sunshine princess prince princesa beautiful pretty hottie babygirl babygirl angel angels flower butterfly purple shadow dragon monkey killer hunter buster ranger tigger tiger
crack crackme crackthis canyoucrackthis hash hashme hashcat hashing hashbrown hashbrowns salted salty salt saltandpepper pepper encryption decrypt decryption encrypted crypto cryptography cryptocurrency cybersecurity security secure insecure algorithm cipher plaintext cleartext digest checksum sha sha1 sha256 sha512 sha3256 md5 ripemd128 ripemd256 haval256 gost snefru whirlpool blake2 johntheripper rockyou rainbowtable brute force bruteforce hacker hacking hackerman hacktheplanet flag capturetheflag ctf ctflearn congratulations success winner solved solution challenge
correcthorsebatterystaple correct-horse-battery-staple opensesame opensaysme youwillneverguess thisisapassword thisismypassword passwordispassword passwordplease usehashcat johnny5 Tr0ub4dor&3 P@ssw0rd p@ssword p@ssw0rd pa55word p455word p455w0rd passw0rd password! password01 password007 password69 password111 password666 password2020 password2021 password2022 password2023 password2024 password2025
baseball football soccer hockey basketball tennis golfer golf softball volleyball rugby cricket lacrosse wrestling boxing racing nascar yankees lakers cowboys steelers raiders eagles arsenal liverpool chelsea rangers redsox redskins broncos dolphins patriots packers giants mustang corvette camaro ferrari porsche mercedes toyota honda yamaha harley ford chevy
superman batman spiderman spider ironman hulk thor loki joker robin flash starwars star trek startrek ncc1701 vader yoda gandalf frodo hobbit merlin wizard magic pokemon pikachu naruto sakura dragonball matrix terminator rocky rambo shrek snoopy scooby spongebob mickey minnie barbie tinkerbell poohbear harrypotter hogwarts twilight vampire zombie minecraft fortnite
metallica eminem nirvana beatles queen prince madonna blink182 slipknot slayer pantera music guitar fender player playboy adidas nike samsung apple iphone android windows linux ubuntu computer internet gateway compaq dell google facebook twitter youtube discord
michael jennifer jessica david james john robert daniel william joseph thomas charles christopher matthew anthony mark donald steven paul andrew joshua kenneth kevin brian george timothy ronald edward jason jeffrey ryan jacob gary nicholas eric stephen jonathan larry justin scott brandon benjamin samuel gregory frank alexander raymond patrick jack dennis jerry tyler aaron jose adam nathan henry douglas zachary peter kyle walter ethan jeremy harold keith christian roger noah gerald carl terry sean austin arthur lawrence jesse dylan bryan joe jordan billy bruce albert willie gabriel logan alan juan wayne roy ralph randy eugene vincent russell louis philip bobby johnny bradley
mary patricia linda barbara elizabeth susan jessica sarah karen nancy lisa margaret betty sandra ashley dorothy kimberly emily donna michelle carol amanda melissa deborah stephanie rebecca laura sharon cynthia kathleen amy shirley angela helen anna brenda pamela nicole samantha katherine emma ruth christine catherine debra rachel carolyn janet virginia maria heather diane julie joyce victoria kelly christina joan evelyn lauren judith megan cheryl andrea hannah martha jacqueline frances gloria ann teresa kathryn sara janice jean alice madison doris abigail julia judy grace denise amber marilyn beverly danielle theresa sophia marie diana brittany natalie isabella charlotte rose alexis kayla jasmine destiny tiffany chelsea holly erica courtney brooke alicia allison alyssa april carmen carrie casey claire crystal cindy felicia jenny jenna katie lori misty monica natasha shannon taylor tracy vanessa wendy
cookie chocolate cheese peanut banana orange apple cherry strawberry coffee cocacola pepsi pizza chicken muffin cupcake candy sugar honey ginger pumpkin potato potatoes cabbage lemon beer tequila whiskey vodka martini
black white blue green red yellow orange purple pink silver golden gold brown gray grey dark light midnight morning summer winter spring autumn monday friday january february march april may june july august september october november december
cat dog bigdog bulldog puppy kitty kitten rabbit bunny bear panda koala monkey gorilla tiger lion panther leopard cheetah jaguar wolf fox eagle falcon hawk raven shark dolphin whale fish fishing turtle cobra python scorpion spider dragon dinosaur unicorn phoenix monster
awesome amazing cool lucky happy smile sweety sweetie sweetheart sexy naughty dirty hardcore extreme crazy insane wicked badboy goodgirl bigdaddy bigdick bigtits booboo bubbles biteme blowme fuck fuckyou fuckme fuckoff asshole bitch pussy sex sexytime panties mother motherfucker
money dollar diamond crystal freedom justice liberty america london paris boston chicago dallas austin marina dakota texas california canada mexico brazil argentina spain italy russia china japan tokyo ireland scotland heaven paradise destiny eternity infinity inevitable unforgettable unbelievable unbreakable invincible fearless warrior knight ninja samurai pirate cowboy soldier marine
alpha beta gamma delta omega apollo atlas zeus hercules caesar viking thunder lightning storm fire water earth wind power energy quantum galaxy planet space moon star stars solar cosmic universe world hello goodbye please thanks thankyou yes no maybe nothing something anything everything
random entropy unique private public hidden unknown anonymous nobody somebody nobodyknows god jesus christ angel demon devil satan church bible faith hope charity peace war life death alive dead dream dreams memory future past today tomorrow yesterday time clock key keys keymaster unlock locked open close door house home school college university student teacher science math physics chemistry biology engineering code coder coding program programmer developer software hardware network server database data information
harambe nootnoot yeet meme memes lol lmao rofl swag yolo swaggy boomer zoomer boomerang klaster ghbdtn thx1138 marina diablo hardcore junior senior junior1 secret1 dragon1 monkey1 sunshine1 princess1 football1 baseball1 soccer1 master1 admin1 root1
'''

roots = []
root_seen = set()

def add_root(value):
    value = value.strip()
    if value and value not in root_seen:
        root_seen.add(value)
        roots.append(value)

for token in root_blob.split():
    add_root(token)

for name in ('sha256', 'sha-256', 'SHA256', 'SHA-256', 'ripemd256', 'haval256', 'snefru256', 'gost', 'sm3', 'blake2s', 'sha3256', 'sha512256'):
    add_root(name)

doc_words = [w for w in re.findall(r'[A-Za-z0-9_-]+', readme) if len(w) <= 24]
for word in doc_words:
    add_root(word)
for i in range(len(doc_words) - 1):
    add_root(doc_words[i] + doc_words[i + 1])
    add_root(doc_words[i] + '_' + doc_words[i + 1])
for i in range(len(doc_words) - 2):
    add_root(doc_words[i] + doc_words[i + 1] + doc_words[i + 2])

phrase_groups = (
    ('can', 'you', 'crack', 'this'),
    ('crack', 'the', 'hash'),
    ('you', 'cracked', 'the', 'hash'),
    ('congratulations', 'you', 'cracked', 'it'),
    ('salt', 'and', 'pepper'),
    ('hashes', 'are', 'not', 'encryption'),
    ('never', 'use', 'sha256', 'for', 'passwords'),
    ('i', 'love', 'cryptography'),
    ('crypto', 'is', 'fun'),
    ('capture', 'the', 'flag'),
    ('use', 'hashcat'),
    ('john', 'the', 'ripper'),
    ('this', 'is', 'the', 'password'),
    ('the', 'password', 'is', 'password'),
    ('easy', 'peasy', 'lemon', 'squeezy'),
    ('correct', 'horse', 'battery', 'staple')
)
for group in phrase_groups:
    for separator in ('', '_', '-', ' '):
        add_root(separator.join(group))

def basic_forms(root):
    values = []
    seen = set()
    lower = root.lower()
    collapsed = ''.join(c for c in root if c not in '_-. ')
    translated = lower.translate(str.maketrans('aeiostlgb', '431057198'))
    alt_map = {'a':'@', 'e':'3', 'i':'!', 'o':'0', 's':'$', 't':'7'}
    alt = ''.join(alt_map.get(c, c) for c in lower)
    for value in (root, lower, root.upper(), root.capitalize(), root.title(), collapsed,
                  collapsed.lower(), translated, alt, lower[::-1]):
        if value and value not in seen:
            seen.add(value)
            values.append(value)
    return values

for root in roots:
    for candidate in basic_forms(root):
        check_extended(candidate)

common_suffixes = [
    '', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '01', '007',
    '10', '11', '12', '13', '21', '22', '23', '42', '69', '99', '101',
    '111', '123', '321', '666', '777', '789', '999', '000', '1234',
    '4321', '12345', '123456', '!', '!!', '@', '#', '$', '?', '1!', '123!'
] + [str(year) for year in range(1940, 2031)]

for root in roots:
    if not root.isalpha():
        continue
    for base in (root.lower(), root.capitalize()):
        for suffix in common_suffixes:
            check_direct_methods(base + suffix)
        for prefix in common_suffixes[:35]:
            check_direct_methods(prefix + base)

leet_maps = (
    {'a':'4', 'e':'3', 'i':'1', 'o':'0', 's':'5', 't':'7', 'l':'1', 'g':'9', 'b':'8'},
    {'a':'@', 'e':'3', 'i':'!', 'o':'0', 's':'$', 't':'7'}
)
for root in roots:
    word = root.lower()
    if not word.isalpha() or len(word) > 18:
        continue
    generated = set()
    for mapping in leet_maps:
        positions = [i for i, c in enumerate(word) if c in mapping]
        if len(positions) > 9:
            positions = positions[:9]
        for mask in range(1, 1 << len(positions)):
            chars = list(word)
            for bit, pos in enumerate(positions):
                if mask & (1 << bit):
                    chars[pos] = mapping[chars[pos]]
            generated.add(''.join(chars))
    for candidate in generated:
        check_primary(candidate)
        for suffix in ('1', '123', '!', '2024', '2025'):
            check_primary(candidate + suffix)

prefixes = ('un', 're', 'super', 'mega', 'ultra', 'dark', 'black', 'white', 'my', 'the', 'mr', 'little')
endings = ('s', 'es', 'ed', 'er', 'ers', 'ing', 'ly', 'y', 'ie', 'ies', 'ness', 'ment', 'able', 'ful', 'less', 'tion')
for root in roots:
    word = root.lower()
    if not word.isalpha() or not 3 <= len(word) <= 14:
        continue
    check_primary(word + word)
    for ending in endings:
        check_primary(word + ending)
    for prefix in prefixes:
        check_primary(prefix + word)

pair_words = []
pair_seen = set()
for root in roots:
    word = root.lower()
    if word.isalpha() and 1 < len(word) <= 12 and word not in pair_seen:
        pair_seen.add(word)
        pair_words.append(word)
for a in pair_words:
    for b in pair_words:
        check_primary(a + b)
for a in pair_words[:120]:
    for b in pair_words[:120]:
        check_primary(a + '_' + b)
        check_primary(a + '-' + b)

for root in pair_words:
    for number in range(10000):
        check_primary(root + str(number))

for length in range(1, 6):
    for chars in itertools.product(string.ascii_lowercase, repeat=length):
        check_primary(''.join(chars))

short_alphabet = string.ascii_letters + string.digits
for length in range(1, 5):
    for chars in itertools.product(short_alphabet, repeat=length):
        check_primary(''.join(chars))

for number in range(100000000):
    check_primary(str(number))

fallback_alphabet = string.ascii_letters + string.digits + string.punctuation + ' '
for length in itertools.count(1):
    for chars in itertools.product(fallback_alphabet, repeat=length):
        check_primary(''.join(chars))
