from rsa_key import RsaKey
from primes import gen_prime
from gcd import gcd, extended_euclid
from random import randint
from int_ptr import IntPtr

def gen_rsa_key() -> RsaKey:
    p = gen_prime()
    q = gen_prime()
    n = p * q
    m = (p - 1) * (q - 1)
    e = 2 ** 16 + 1

    '''
    d = n
    while gcd(d, n) != 1:
        d = randint(3, m)
    '''
    # Find d
    x = IntPtr(-1)
    y = IntPtr(-1)
    assert extended_euclid(e, m, x, y) == 1
    d = x.val

    assert (e * d) % m == 1

    return RsaKey(p, q, e, d)
