from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
# But DSS works with DSA keys.
# For ECDSA, you can use the module `Crypto.Signature.EC`? Not sure.