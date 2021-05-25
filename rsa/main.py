import os

from rsa_key import PrivateRsaKey, RsaKey
from primes import gen_prime
from gcd import gcd
from gen_rsa_key import gen_rsa_key

rsa_key = gen_rsa_key()
public_rsa_key = rsa_key.public_key()
private_rsa_key = rsa_key.private_key()

encrypted = public_rsa_key.encrypt(org_bytes)
decrypted = private_rsa_key.decrypt(encrypted)

assert decrypted == org_bytes, f"RsaKey: {rsa_key}"
