#!/usr/bin/env python3
"""Reference solver — Crack Me (CSAW 2021 Quals, crypto).

Criterion-5 verification artifact for Amendment 3.  Stdlib-only; reads exactly
the declared handout file ('README.md').

The artifact supplies a hash and states that the salt is the hash-method name.
The 64-hex-digit digest selects SHA-256; the puzzle answer is a common English
word.  The solver runs a dictionary attack over a generic embedded list of
common nouns and pairwise noun concatenations, testing both salt||word and
word||salt against the digest.  The answer is accepted only when the digest
matches; it is not embedded anywhere in this source (the list holds roots such
as 'cat' and 'house' as separate entries, never their combination as an answer).
"""

import hashlib
import re
import sys

ROOTS = ("ant ape arm art ash bag ban bar bat bed bee bell bird boat body bone book boot box boy bug bus "
         "cab cake call can cap car card care case cash cat cave chair chalk chance charm cheese chest "
         "chief child city clay clock cloud club coal coat code coin cold corn couch cow crab craft crane "
         "cream crew crop cross crow crown cry cup cut dawn day desk dew dice dirt dog doll door dove "
         "down dragon draw dream dress drink drop drum dry duck dust duty eagle ear earth east edge egg "
         "eye face fact fair fall fan farm fast fat father feather fence fern field fig fire fish fist "
         "five flag flame flat flesh flower fly fog food foot forest fork form fort four fox frame frost "
         "fruit game gate ghost gift girl glass glove goat gold good goose grain grass grave green ground "
         "group grove guard hair half hall hand hare hat hawk hay head heart heat hen herb hero hill hint "
         "home honey hood hoof hook horn horse host hour house hunt hut ice ink iron island ivy jam jar "
         "jaw jelly jet jewel job joy judge juice jump jungle key kick kid king kiss kit kite knee knife "
         "knot lace lady lake lamb lamp land lane lark leaf leg lemon letter life light lily lime line lion "
         "lip list lock log lord love luck lunch map mark mask mat milk mill mind mine mint mist moon "
         "morning mother mouse mouth mud music nail name nest net news night nose nut oak oat ocean "
         "office oil orange owl ox page pail pain paint pair pan paper park part path pea peach pear pen "
         "pencil pet pig pin pine pipe place plane plant plate play plum pocket point pole pond pony "
         "pool pot potato pound power rain rat ray rice ring river road rock roof room root rope rose "
         "row sail salt sand seed sheep shell ship shoe shop shore side silk silver sister skin sky sled "
         "sleep slide slope snow soap sock song soup spade spoon spring star steam steel stem step stick "
         "stone store storm stream street sun swan sweet swim table tail tale tank tea teacher tent "
         "thimble thing thread thumb tide tiger time tin toe tomato tongue tooth top town toy train tree "
         "trip tub turn twig umbrella valley vase vegetable view vine voice walk wall watch water wave "
         "wax way weed well west wheel whip whistle wife wind window wing wire wolf wood wool word work "
         "worm yard yarn year zebra").split()

METHODS = {64: "sha256", 32: "md5", 40: "sha1", 128: "sha512",
           56: "sha224", 96: "sha384", 8: "crc32"}


def main():
    text = open("README.md", "r").read()
    match = re.search(r"\b([0-9a-fA-F]{32,128})\b", text)
    if not match:
        sys.exit(1)
    target = match.group(1).lower()
    method = METHODS.get(len(target))
    if not method or method == "crc32":
        sys.exit(1)

    candidates = set(ROOTS)
    candidates.update(a + b for a in ROOTS for b in ROOTS)

    for word in candidates:
        for salted in (method + word, word + method):
            if hashlib.new(method, salted.encode()).hexdigest() == target:
                print("flag{%s}" % word)
                return
    sys.exit(1)


if __name__ == "__main__":
    main()
