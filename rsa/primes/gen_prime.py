from random import randint

def gen_prime() -> int:
    from .sieve import sieve_singleton
    return sieve_singleton.primes[randint(0, len(sieve_singleton.primes) - 1)]
