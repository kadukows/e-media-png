from rsa_key import RsaKey
from primes import gen_prime
from gcd import gcd
from gen_rsa_key import gen_rsa_key

for i in range(10):
    a = gen_prime()
    b = gen_prime()

    print(f'gcd({a}, {b}): ', gcd(a, b))

    rsa_key = gen_rsa_key()
    print(rsa_key, f"n.bit_length(): {rsa_key.n.bit_length()}")
