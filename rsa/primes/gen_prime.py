from random import randint
from  Crypto.Util.number import getPrime

def gen_prime() -> int:
    from .sieve import sieve_singleton
    return getPrime(48)
