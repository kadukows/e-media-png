from rsa_key import RsaKey
from primes import gen_prime
from gcd import gcd, extended_euclid
from random import randint
from int_ptr import IntPtr

def gen_rsa_key() -> RsaKey:
    p = gen_prime()
    q = gen_prime()
    m = (p - 1) * (q - 1)
    e = 2 ** 16 + 1

    # Find d
    x = IntPtr(0)
    y = IntPtr(0)
    assert extended_euclid(e, m, x, y) == 1
    d = x.val

    assert (e * d) % m == 1

    return RsaKey(p=p, q=q, e=e, d=d)
