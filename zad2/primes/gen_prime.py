from random import randint

def gen_prime() -> int:
    from . import _PRIMES
    return _PRIMES[randint(0, len(_PRIMES) - 1)]
