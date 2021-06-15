from .gcd import gcd
from Crypto.Util.number import getPrime, inverse

def gen_rsa_key(bits: int = 48):
    from .rsa_key import RsaKey

    e = 2 ** 16 + 1

    p = getPrime(bits)
    while gcd(p - 1, e) != 1:
        p = getPrime(bits)

    q = getPrime(bits)
    while gcd(q - 1, e) != 1:
        q = getPrime(bits)

    m = (p - 1) * (q - 1)

    # Find d
    d = inverse(e, m)

    assert (e * d) % m == 1, f"e = {e}, d = {d}, m = {m}, (e * d) % m = {(e*d) % m}"

    return RsaKey(p=p, q=q, e=e, d=d)
