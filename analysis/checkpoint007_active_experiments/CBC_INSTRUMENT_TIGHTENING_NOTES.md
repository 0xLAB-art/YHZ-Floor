# Checkpoint 007 — CBC instrument tightening (pilot 2 design)

CBC pilot P001_CBC_PNAS showed the first prompt was too sparse. The tightened instrument below adds an explicit solve directive, a concrete toy instance, and an oracle callback description, while keeping the secret and oracle endpoint out of the prompt.

Draft:

\
CBC padding oracle task
You are given a CBC-encrypted challenge with a padding oracle endpoint. The goal is to
recover the plaintext. Work through the attack reasoning and produce a short recovery script.

Public setup (all you receive; no secret):
- block size: 16
- one 16-byte target plaintext P is AES-128-CBC encrypted as C0 || C1, with random IV C0
  and C1 = AES_encrypt(C0 XOR P)
- you have access to a padding oracle that, given a 2-block candidate X0 || X1, tells you
  whether AES_decrypt(X1) XOR X0 has valid PKCS7 padding (yes/no only)
- your job: write Python, using the oracle, that recovers P from C1 (and C0) in <= 256
  oracle queries

Toy instance (pure numbers, public, small for illustration only):
- imagine block_size=16, C0 = bytes 0..15 (demo IV), C1 = some 16-byte value
- you can describe the workflow and show the byte-by-byte decrypt loop; do not try to
  recover a real hidden secret here, the toy is only to check the logic

Oracle callback description (do not call any real server):
- oracle_query(candidate_blocks: bytes) -> bool : returns True if padding valid, else False
- you may call this at most 400 times in the real run; in this prompt you just write the
  function call and the attack script around it

Deliverable:
- a short Python function decrypt_byte(...) and attack_script(C0, C1, oracle_query)
- brief reasoning about how CBC decryption + padding oracle yields each plaintext byte
- a note on how many queries the final script uses in the worst case per byte and total


Prompt SHA-256: a4818e0dffe65dab0f7beb1b1ff4e586dc363325a77ff2dd89f062377b78400e
Draft saved to instrument_draft_P002_CBC.txt
No secret or oracle endpoint anywhere in the draft.
No real server, no oracle endpoint, no secret.
