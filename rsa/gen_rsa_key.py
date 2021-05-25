from rsa_key import RsaKey
from primes import gen_prime
from gcd import gcd, extended_euclid, modInverse
from random import randint
from int_ptr import IntPtr

def gen_rsa_key() -> RsaKey:
    n = 1
    while (n.bit_length() - 1) / 8 < 1:
        p = gen_prime()
        q = gen_prime()
        n = p * q

    m = (p - 1) * (q - 1)
    e = 2 ** 16 + 1

    # Find d
    d = modInverse(e, m)

    assert (e * d) % m == 1

    return RsaKey(p=p, q=q, e=e, d=d)
