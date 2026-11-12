import hashlib
import itertools
import re
import string
import sys

with open('README.md', 'r', encoding='utf-8') as f:
    TARGET = bytes.fromhex(re.search('[0-9A-Fa-f]{64}', f.read()).group(0))

SALT = b'sha256'
PREFIX = hashlib.sha256(SALT)


def win(s):
    sys.stdout.write('flag{' + s + '}' + chr(10))
    raise SystemExit(0)


def check(s):
    b = s.encode('utf-8')
    if hashlib.sha256(b + SALT).digest() == TARGET:
        win(s)
    h = PREFIX.copy()
    h.update(b)
    if h.digest() == TARGET:
        win(s)


def hmac256(key, message):
    if len(key) > 64:
        key = hashlib.sha256(key).digest()
    key += bytes(64 - len(key))
    inner = bytes(x ^ 54 for x in key)
    outer = bytes(x ^ 92 for x in key)
    return hashlib.sha256(outer + hashlib.sha256(inner + message).digest()).digest()


method_map = {}
for method_name in sorted(hashlib.algorithms_available):
    try:
        probe = hashlib.new(method_name)
    except (ValueError, TypeError):
        continue
    if getattr(probe, 'digest_size', 0) != 32:
        continue
    normalized = ''.join(c for c in method_name.lower() if c.isalnum()).encode()
    if normalized not in method_map:
        labels = [normalized, method_name.lower().encode()]
        if normalized == b'sha256':
            labels += [b'sha256', b'sha2256', b'sha2', b'sha-256', b'sha_256', b'SHA256', b'SHA-256']
        elif normalized == b'sha3256':
            labels += [b'sha3256', b'sha3-256', b'sha3_256']
        elif normalized == b'blake2s':
            labels += [b'blake2s', b'blake2256', b'blake2s256']
        method_map[normalized] = (method_name, tuple(dict.fromkeys(labels)))
METHODS = list(method_map.values())
WIDE_SEEN = set()


def wide(s):
    if s in WIDE_SEEN:
        return
    WIDE_SEEN.add(s)
    b = s.encode('utf-8')
    tails = (b'', bytes((10,)), bytes((13, 10)))
    for name, labels in METHODS:
        try:
            if hashlib.new(name, b).digest() == TARGET:
                win(s)
        except (ValueError, TypeError):
            continue
        for label in labels:
            for separator in (b'', b':', b'$', b'_', b'-'):
                left = b + separator + label
                right = label + separator + b
                for tail in tails:
                    try:
                        if hashlib.new(name, left + tail).digest() == TARGET:
                            win(s)
                        if hashlib.new(name, right + tail).digest() == TARGET:
                            win(s)
                    except (ValueError, TypeError):
                        pass
    if hmac256(SALT, b) == TARGET or hmac256(b, SALT) == TARGET:
        win(s)
    inner = hashlib.sha256(b).digest()
    inner_hex = inner.hex().encode()
    for representation in (inner, inner_hex):
        for payload in (representation, representation + SALT, SALT + representation):
            if hashlib.sha256(payload).digest() == TARGET:
                win(s)
    for encoding in ('utf-16le', 'utf-16be'):
        for text in (s, s + 'sha256', 'sha256' + s):
            if hashlib.sha256(text.encode(encoding)).digest() == TARGET:
                win(s)


RAW = r'''
example crackme crackthis sha256 hash hashing hashcat password password1 password12 password123 password1234 password12345 Password Password1 Password123 P@ssword P@ssw0rd P@ssw0rd1 p@ssword p@ssw0rd pa55word pa$$word passw0rd passw0rd1 passwd pass pass123
123456 12345 123456789 1234567 12345678 1234567890 1234 123 12 1 654321 111111 000000 666666 121212 112233 555555 789456 999999 11111 7777777 159753 222222 987654 00000 55555 123321 888888 456789 0123456789 789456123 123654 777777 101010 696969 131313 232323 102030 147258 147258369 258369 741852 741852963 951753 753159 852456 987654321 13579 24680 111222 333333 444444 88888888 99999999 123123 321321 123abc abc123 abcd1234 a1b2c3 q1w2e3r4 q1w2e3r4t5 1q2w3e4r 1q2w3e4r5t 1qaz2wsx zaq12wsx qazwsx wsxedc rfvtgb 1qazxsw2 1234qwer
qwerty qwerty1 qwerty12 qwerty123 qwertyui qwertyuiop asdf asdfgh asdfghjkl zxcv zxcvbn zxcvbnm qazxsw edcrfv tgbnhy yhnujm ujmikol qaz123 keyboard keyboard1
iloveyou iloveu iloveyou1 iloveyou2 iloveme loveyou loveme love love1 love123 lover lovers lovely mylove forever always together soulmate sweetheart sweetie sweety darling honey kisses kissme precious beautiful beauty pretty hottie hotstuff sexy sexylady cutie cutiepie babygirl babygirl1 babygurl babyboy booboo bubbles butterfly flower flowers sunshine rainbow diamond angel angels angel1 princess princess1 princesa prince tinkerbell tweety poohbear hellokitty
letmein letmein1 welcome welcome1 welcome123 admin admin1 administrator root toor guest login access access1 secret secret1 changeme default system manager master trustno1 trustme trust nobody noone god jesus jesus1 jesusfreak freedom computer internet matrix testing test test123 demo user user1 superuser oracle linux windows microsoft apple google yahoo samsung nokia motorola dell cisco server database network wireless wifi router modem secure security crypto cryptography encryption decryption cipher salted salt salty pepper algorithm checksum digest sha md5 sha1 sha512 ripemd crack cracker cracked cracking challenge flag ctf cyber hacker hacking hackme hacktheplanet pentest kali metasploit nmap wireshark openwall johntheripper rockyou wordlist brute bruteforce
hunter hunter2 dragon monkey shadow killer buster ranger mustang harley corvette thunder lightning storm fire flame phoenix tiger tigers lion lions panther jaguar leopard cheetah bear wolf wolves eagle falcon hawk shark dolphin whale penguin turtle rabbit bunny horse horses chicken rooster puppy dog dogs kitty kitten cat cats mouse bird snake cobra viper spider scorpion dinosaur rex godzilla monster beast demon devil angel unicorn pegasus
rockyou nicole daniel jessica michael ashley michelle tigger chocolate soccer anthony friends purple jordan liverpool justin fuckyou football andrea carlos jennifer joshua superman hannah amanda basketball andrew elizabeth charlie samantha barbie chelsea jasmine brandon melissa eminem matthew robert danielle family jonathan whatever vanessa cookie naruto summer spongebob joseph junior softball taylor yellow daniela lauren mickey alexandra alexis estrella miguel william thomas angela patrick sakura adrian alexander destiny christian sayang america dancer monica richard carolina steven rangers louise orange shorty nathan snoopy gabriel cherry sandra alejandro george brittany alejandra patricia rachel tequiero cheese arsenal antonio heather david ginger stephanie peanut blink182 victoria fernando pokemon maggie corazon cristina manuel myspace rebelde ricardo heaven baseball martin greenday november alyssa madison mother mahalkita batman september december morgan maria gabriela bailey jeremy pamela kimberly gemini shannon pictures asshole sophie jessie claudia angelica austin mauricio victor tiffany mariana eduardo andres courtney ronaldo october inuyasha peaches veronica chris adriana james banana crystal celtic edward oliver diana angelo kenneth scooby carmen sebastian rebecca jackie spiderman christopher karina johnny school barcelona august orlando samuel cameron slipknot bonita kevin maganda casper brenda adidas karen isabel natalie javier sarah bowwow portugal laura marvin denise jasper rockstar january alicia nicholas cristian tintin bianca chrisbrown chichi bubba marley tupac friendster andrey dante million shelby squirt guitar nicolas paramore shakira lollypop molly johncena marcos chanel armando dominique oscar lakers marcelo jesse
fuck fucker fucking fuckoff fuckyou1 bitch bitches asshole asswipe bastard bullshit shit shitty pussy dick cock boobs boobies playboy porn porno sex sex123 suckme biteme kissmyass motherfucker
john jon johnny jonathan joseph joe joey james jim jimmy jack jackson jason jacob jake jeremy jerry jeff jeffrey josh joshua justin jordan julian jude juan jose jesus jorge julio carlos charles chris christian christopher cameron connor cody cole colin craig curtis caleb kevin kenneth kyle kurt karl brian bryan brandon brad bradley ben benjamin bill billy bob bobby robert robbie ryan richard rick ricky raymond ron ronald randy russell roger roy ross ruben rafael ricardo raul rodney roman
michael mike matt matthew mark marc martin marvin mario marcos manuel miguel max maxwell mason nathan nicholas nick nicolas noah oliver oscar owen patrick paul peter philip phillip sam samuel scott sean shawn steven stephen steve thomas tim timothy todd tom tommy tony travis trevor tyler victor vincent walter wayne william zach zachary adam adrian alan albert alex alexander andrew anthony antonio aaron abraham eric edward eddie ethan evan frank frankie fred freddy gabriel george greg gregory henry harry hugo isaac ivan david daniel dennis derek dominic douglas dustin dylan elijah felix fernando francisco gary gerald gilbert grant harold hector howard hunter ian isaiah jaime jared jasper
mary maria marie mariah michelle melissa megan meghan margaret maggie madison morgan monica molly maya mia miriam natalie nicole nancy nina olivia pamela patricia paula rachel rebecca renee rose ruby sabrina samantha sandra sara sarah shannon sharon shelby sophia sophie stephanie susan suzanne tanya taylor teresa theresa tiffany tina valerie vanessa veronica victoria violet wendy whitney zoe
jessica jennifer julia julie juliana jasmine janet jane jenny joanna jordan josephine joy joyce judith judy karen karina katherine kathleen kathryn katie kayla kelly kim kimberly kristen kristin kristina laura lauren leah leslie linda lisa liz lindsay lori louise lucy maria mariana marissa amanda amber amy andrea angela angelica anna anne annie ashley alyssa alexa alexandra alexis alicia allison april audrey autumn barbara becky beth bethany bianca brandy brenda brittany brooke carla carmen carol caroline carolina carrie cassandra catherine charlotte chelsea cheryl christina christine cindy claire claudia courtney crystal daniela danielle dawn deborah debra denise destiny diana donna dorothy elizabeth emily emma erica erin eva evelyn faith felicity gabriela grace hannah hayley heather helen holly isabel isabella jackie jacqueline
smith johnson williams brown jones miller davis garcia rodriguez wilson martinez anderson thomas hernandez moore jackson thompson white lopez lee gonzalez harris clark lewis robinson walker perez hall young allen sanchez wright king scott green baker adams nelson hill ramirez campbell mitchell roberts carter phillips evans turner torres parker collins edwards stewart flores morris nguyen murphy rivera cook rogers peterson cooper reed bell gomez kelly howard ward cox diaz richardson wood watson brooks bennett gray reyes cruz hughes price myers long foster sanders morales powell sullivan ortiz jenkins perry butler barnes fisher henderson coleman simmons patterson reynolds hamilton graham ramos wallace griffin west hayes chavez gibson bryant ellis stevens murray ford marshall owens harrison ruiz kennedy wells alvarez woods mendoza castillo olson webb washington tucker freeman burns vasquez snyder simpson crawford porter shaw gordon wagner romero hicks dixon hunt palmer robertson black holmes stone meyer boyd mills warren fox rice schmidt patel ferguson nichols medina ryan fernandez weaver daniels gardner payne dunn pierce arnold spencer peters hawkins grant castro hoffman hart elliott cunningham knight carroll hudson duncan armstrong berry andrews johnston lane riley carpenter perkins silva richards willis matthews chapman lawrence watkins wheeler larson carlson harper greene burke morrison jacobs lawson franklin lynch bishop salazar montgomery harvey howell dean weber garrett burton fuller mccoy welch walters reid walsh little fowler bowman davidson schneider newman brewer holland banks curtis pearson douglas barrett hopkins keller stanley bates beck wade barnett caldwell lambert powers chambers craig leonard lowe rhodes byrd gregory shelton frazier becker sutton cohen jennings parks watts barker norris vaughn holt steele benson neal horton terry wolfe hale lyons graves haynes miles warner bush thornton mann zimmerman erickson fletcher page dawson reeves klein baldwin moran robbins higgins ball
red blue green yellow orange purple pink black white brown gray grey silver gold golden violet indigo crimson scarlet aqua cyan magenta turquoise rainbow dark light bright color
apple orange banana grape cherry strawberry blueberry raspberry blackberry watermelon melon lemon lime peach peaches pear pineapple mango coconut kiwi papaya avocado potato tomato carrot onion garlic pepper pumpkin cookie cookies chocolate candy sugar honey coffee tea beer whiskey whisky vodka tequila rum wine pepsi coke sprite pizza burger hamburger cheeseburger hotdog chicken bacon sausage cheese sandwich taco burrito sushi noodle noodles rice beans cake cupcake donut pancake waffle popcorn peanut butter jelly cinnamon ginger vanilla strawberry
football baseball basketball soccer hockey tennis golf golfer rugby cricket volleyball softball bowling boxing wrestling karate judo running swimming skating snowboarding surfing fishing hunting racing nascar formulaone sports champion winner yankees cowboys dallas lakers celtics rangers arsenal chelsea liverpool barcelona realmadrid manchester united juventus milan inter bayern dolphins patriots steelers packers broncos raiders giants jets eagles falcons panthers saints vikings bears lions tigers cardinals cubs bulls rockets spurs warriors
america american usa canada canadian mexico brazil brasil argentina chile peru colombia venezuela portugal spain france italy germany england ireland scotland wales russia china japan korea india pakistan australia africa europe london paris madrid rome berlin moscow tokyo sydney miami dallas houston austin boston chicago seattle denver phoenix atlanta orlando vegas california texas florida ohio maryland virginia georgia alabama alaska arizona colorado montana kansas kentucky louisiana michigan minnesota mississippi missouri nevada oregon carolina tennessee washington baltimore newyork brooklyn queens bronx hollywood
monday tuesday wednesday thursday friday saturday sunday january february march april may june july august september october november december spring summer autumn winter christmas xmas halloween easter birthday happybirthday newyear valentine holiday vacation weekend morning afternoon evening midnight today tomorrow yesterday
starwars startrek matrix terminator predator alien aliens batman superman spiderman ironman hulk thor loki joker robin wonderwoman avengers marvel dccomics transformers pokemon pikachu naruto sasuke sakura dragonball dragonballz goku vegeta inuyasha anime disney mickey minnie donald goofy pluto cinderella frozen shrek spongebob simpsons familyguy southpark scooby scoobydoo harrypotter hogwarts hermione voldemort dumbledore twilight titanic avatar gladiator rocky rambo godfather scarface pulpfiction jurassicpark lordoftherings lotr hobbit
metallica nirvana beatles queen coldplay radiohead greenday linkinpark blink182 slipknot paramore evanescence falloutboy goodcharlotte mychemicalromance panicatthedisco systemofadown disturbed korn acdc aerosmith bonjovi gunsnroses ledzeppelin pinkfloyd rollingstones eminem tupac drake rihanna beyonce shakira madonna britney christina usher enrique justinbieber mileycyrus selena arianagrande one direction onedirection
music guitar piano drums violin singer dancer dance rock punk metal jazz blues hiphop rap reggae song songs melody band concert movie cinema picture pictures camera photo photos video games gaming gamer xbox playstation nintendo sega minecraft fortnite warcraft dota counterstrike halo mario sonic zelda
hello helloworld hi goodbye please thanks thankyou sorry yes no maybe whatever anything nothing something everything someone nobody everybody awesome amazing wonderful perfect fantastic excellent brilliant beautiful gorgeous lucky crazy funny happy happiness smile laughing dream dreams hope faith peace life live laugh truth honest honesty loyal loyalty respect courage power strong strength victory success winner money cash dollar million billionaire work home house school college university student teacher family mother father mom mommy dad daddy sister brother cousin grandma grandpa friend friends bestfriend
one two three four five six seven eight nine ten eleven twelve first second third zero alpha beta gamma delta omega infinity forever eternal eternity magic magical wizard merlin king queen prince princess knight warrior ninja samurai pirate captain soldier marine army navy airforce police cowboy angel demon ghost spirit heaven hell paradise earth world universe galaxy space star stars moon sun solar venus mars jupiter saturn comet rocket astronaut
big little small tiny giant super mega ultra hyper sweet cute pretty hot sexy cool awesome wicked wild crazy bad good best better great lucky dark black white blue red green golden silver fire ice water wind earth thunder lightning storm shadow night day sunrise sunset midnight northern southern eastern western secret hidden mystery unknown invisible impossible inevitable immortal invincible legendary epic ultimate extreme random simple easy hard difficult smart clever genius stupid silly funny serious
run walk jump fly swim drive ride play game win lose fight kill shoot love hate like want need know think believe trust remember forget dream sleep wake eat drink sing dance laugh smile cry shout whisper open close start stop begin end finish enter leave return come go give take make build break fix find seek look watch see hear listen speak talk write read learn teach help save protect attack defend escape follow lead create destroy change choose try use work rest wait move turn push pull
car cars truck jeep ford chevy toyota honda nissan mazda lexus bmw mercedes audi porsche ferrari lamborghini mustang camaro corvette charger challenger harley motorcycle bike bicycle engine turbo speed fast faster furious road highway route driver racing race
house home bedroom kitchen bathroom garden garage castle palace apartment room door window table chair couch sofa bed pillow blanket television phone telephone mobile laptop desktop monitor printer scanner keyboard mouse internet email gmail facebook twitter instagram snapchat tiktok youtube myspace friendster
amor amore tequiero quiero corazon princesa principe estrella cielo vida feliz felicidad familia amigo amigos amiga bonitas bonita bonito besos beso dios gracias hola adios libertad futbol mexico brasil senha segredo saudade mahal mahalkita sayang cinta kasih aku kamu salamat mabuhay
umbc UMBC DawgCTF dawgCTF CyberDawgs cyberdawgs cyberdawg cyberdogs dawg dawgs doggo doge bork woof ruff pupper puppers retriever retrievers chesapeake maryland baltimore goodboy goodboi gooddog whosagoodboy whosagoodboi saltydog hashbrown hashbrowns saltandpepper securehashalgorithm encryptionmethod hashingisfun saltingisimportant passwordsarebad crackmeifyoucan youwillneverguess nevergonnagiveyouup correcthorsebatterystaple
open sesame opensesame foo bar foobar lorem ipsum loremipsum sample example demo testing qwertyuiopasdfghjkl abcdef abcdefg abcdefgh abcdefghij abcdefghijklmnopqrstuvwxyz abc12345 abc123456 password! password!! Password! Password1! P@ssw0rd! admin123 adminadmin rootroot secret123 welcomehome welcome12345 letmein123 hello123 helloworld123 love1234 dragon123 monkey123 sunshine123 princess123 master123 football123 baseball123 soccer123 iloveyou123
'''

PHRASES = [
    ('i', 'love', 'you'), ('i', 'love', 'u'), ('love', 'you'),
    ('let', 'me', 'in'), ('never', 'give', 'up'),
    ('never', 'gonna', 'give', 'you', 'up'),
    ('you', 'are', 'my', 'sunshine'), ('happy', 'birthday'),
    ('happy', 'new', 'year'), ('good', 'morning'), ('good', 'night'),
    ('sweet', 'dreams'), ('pretty', 'girl'), ('baby', 'girl'),
    ('baby', 'boy'), ('best', 'friends'), ('forever', 'and', 'always'),
    ('live', 'laugh', 'love'), ('trust', 'no', 'one'),
    ('secret', 'password'), ('correct', 'horse', 'battery', 'staple'),
    ('may', 'the', 'force', 'be', 'with', 'you'), ('hakuna', 'matata'),
    ('carpe', 'diem'), ('all', 'you', 'need', 'is', 'love'),
    ('winter', 'is', 'coming'), ('to', 'be', 'or', 'not', 'to', 'be'),
    ('hello', 'world'), ('foo', 'bar'), ('admin', 'admin'),
    ('salt', 'and', 'pepper'), ('hash', 'brown'), ('hash', 'browns'),
    ('secure', 'hash', 'algorithm'), ('encryption', 'method', 'of', 'the', 'hash'),
    ('crack', 'me'), ('crack', 'this'), ('dawg', 'ctf'),
    ('cyber', 'dawgs'), ('good', 'boy'), ('good', 'dog'),
    ('who', 'is', 'a', 'good', 'boy'), ('whos', 'a', 'good', 'boy')
]

raw = RAW.split()
for parts in PHRASES:
    for separator in ('', ' ', '_', '-', '.'):
        raw.append(separator.join(parts))
    raw.append(parts[0] + ''.join(x.capitalize() for x in parts[1:]))
    raw.append(''.join(x.capitalize() for x in parts))
raw = list(dict.fromkeys(raw))

for candidate in raw:
    for variant in dict.fromkeys((candidate, candidate.lower(), candidate.upper(), candidate.capitalize(), candidate.swapcase())):
        wide(variant)

stems = list(dict.fromkeys(
    candidate.lower() for candidate in raw
    if candidate.isalpha() and 2 <= len(candidate) <= 20
))

prefixes = ('my', 'the', 'super', 'little', 'big', 'baby', 'sweet', 'dark', 'black', 'mr', 'miss', 'king', 'queen')
compound_suffixes = ('boy', 'girl', 'man', 'woman', 'lover', 'love', 'world', 'star', 'dog', 'cat', '123')
for word in stems:
    generated = [word + 's', word + 'es', word + 'ed', word + 'ing', word + 'er', word + 'ly', word + 'ness']
    if word.endswith('e') and len(word) > 2:
        generated.append(word[:-1] + 'ing')
    if word.endswith('y') and len(word) > 2:
        generated += [word[:-1] + 'ies', word[:-1] + 'ier']
    for prefix in prefixes:
        generated.append(prefix + word)
    for suffix in compound_suffixes:
        generated.append(word + suffix)
    for candidate in dict.fromkeys(generated):
        check(candidate)
        check(candidate.capitalize())

LEET_STANDARD = str.maketrans('aeiostbg', '43105789')
LEET_ALTERNATE = str.maketrans({'a': '@', 'e': '3', 'i': '!', 'o': '0', 's': '$', 't': '7', 'b': '8', 'g': '9'})
leet_replacement = {'a': '4', 'e': '3', 'i': '1', 'o': '0', 's': '5', 't': '7', 'b': '8', 'g': '9'}
for word in stems[:700]:
    for candidate in dict.fromkeys((word.translate(LEET_STANDARD), word.translate(LEET_ALTERNATE))):
        check(candidate)
        check(candidate.capitalize())
    positions = [i for i, c in enumerate(word) if c in leet_replacement][:9]
    for mask in range(1, 1 << len(positions)):
        chars = list(word)
        for bit, position in enumerate(positions):
            if mask & (1 << bit):
                chars[position] = leet_replacement[chars[position]]
        check(''.join(chars))

COMBO = '''
password pass word love ilove you my baby girl boy pretty sweet honey angel princess prince dragon monkey shadow sunshine football baseball soccer super man woman bat man spider star wars hello world secret master trust no one happy birthday forever always best friend family good bad dark night fire ice thunder storm blue red black white gold golden silver cyber hacker hash salt pepper crack crypto secure dog dawg cat puppy kitty music rock star computer internet killer hunter tiger lion wolf eagle king queen magic wizard ninja pirate warrior mary john michael david daniel jessica ashley nicole
'''.split()
pair_words = list(dict.fromkeys(COMBO + stems[:240]))[:360]
for first in pair_words:
    for second in pair_words:
        check(first + second)
        check(first.capitalize() + second)
        check(first + second.capitalize())
        for separator in ('_', '-', '.'):
            check(first + separator + second)

fixed_suffixes = '''
1 2 3 4 5 6 7 8 9 0 01 02 03 07 10 11 12 13 21 22 23 24 42 44 55 66 69 77 88 99 001 007 008 009 101 111 123 321 420 456 555 666 777 789 888 999 000 1234 4321 1111 0000 6969 7777 8888 9999 12345 123456 654321 1234567 12345678 ! !! !!! @ # $ ? . _ !1 !12 !123 1! 123! @1 @123 #1 _1 _123 .1 .123
'''.split()
suffixes = fixed_suffixes + [str(i) for i in range(100)] + [str(i).zfill(2) for i in range(100)] + [str(year) for year in range(1950, 2031)]
suffixes = list(dict.fromkeys(suffixes))
for index, word in enumerate(stems):
    forms = tuple(dict.fromkeys((word, word.capitalize(), word.translate(LEET_STANDARD))))
    for form in forms:
        for suffix in suffixes:
            check(form + suffix)
            if index < 250 and suffix[0].isdigit():
                check(form + '_' + suffix)

for word in stems[:500]:
    forms = tuple(dict.fromkeys((word, word.capitalize(), word.translate(LEET_STANDARD))))
    for form in forms:
        for number in range(1000):
            check(form + str(number))
            if number < 100:
                check(form + str(number).zfill(2))
            check(form + str(number).zfill(3))

for word in stems[:70]:
    for number in range(10000):
        suffix = str(number).zfill(4)
        check(word + suffix)
        check(word.capitalize() + suffix)

for word in stems[:220]:
    for number in range(1000):
        prefix = str(number)
        check(prefix + word)
        if number < 100:
            check(str(number).zfill(2) + word)

for year in range(1950, 2031):
    for month in range(1, 13):
        for day in range(1, 32):
            yyyy = str(year)
            yy = str(year % 100).zfill(2)
            mm = str(month).zfill(2)
            dd = str(day).zfill(2)
            for candidate in (
                mm + dd + yyyy, dd + mm + yyyy, yyyy + mm + dd,
                mm + dd + yy, dd + mm + yy, yy + mm + dd,
                mm + '/' + dd + '/' + yyyy, dd + '/' + mm + '/' + yyyy,
                mm + '-' + dd + '-' + yyyy, dd + '-' + mm + '-' + yyyy
            ):
                check(candidate)

SYLLABLES = '''
ba be bi bo bu ca ce chi co da de di do dra dy el en er fa fi fo ga ge gi go ha he hi ho ja je jo ka ke ki ko la le li lo lu ma me mi mo na ne ni no pa pe pi po ra re ri ro sa se shi so sta ta te ti to tra ty va ve vi wa we wi wo za ze zi zo an ar al on or in ing ly son ton man boy girl love pass word star fire sun moon sky blue red black sweet baby dark light king queen dog cat rock cyber hash salt
'''.split()[:90]
for count in (2, 3):
    for parts in itertools.product(SYLLABLES, repeat=count):
        candidate = ''.join(parts)
        if 3 <= len(candidate) <= 15:
            check(candidate)

alphabet = string.ascii_lowercase + string.digits
for length in range(1, 5):
    for chars in itertools.product(alphabet, repeat=length):
        check(''.join(chars))
for chars in itertools.product(string.ascii_lowercase, repeat=5):
    check(''.join(chars))

raise RuntimeError('verified preimage not reached')
