import os, json

from rsa_key import PrivateRsaKey, RsaKey
from primes import gen_prime
from gcd import gcd
from gen_rsa_key import gen_rsa_key

from dataclasses import asdict

rsa_key = gen_rsa_key(144)
#rsa_key = RsaKey(p=250771626894343, q=205993624686449, e=173085330483383, d=19333608477755356975563845831)
#rsa_key = RsaKey(p=45433, q=49697, e=65537, d=565575425)

public_rsa_key = rsa_key.public_key()
private_rsa_key = rsa_key.private_key()

with open('public.rsa', 'w') as file:
    file.write(json.dumps(asdict(public_rsa_key)))

with open('private.rsa', 'w') as file:
    file.write(json.dumps(asdict(private_rsa_key)))


org_bytes = os.urandom(1024 * 500)
with open('org_bytes', 'wb') as file:
    file.write(org_bytes)


'''
with open('org_bytes', 'rb') as file:
    org_bytes = file.read()
'''


encrypted = public_rsa_key.encrypt(org_bytes)
decrypted = private_rsa_key.decrypt(encrypted)

assert org_bytes == decrypted, f"Rsa key: {rsa_key}"

for i in range(100, 200):
    rsa_key = gen_rsa_key(i)
    org_bytes = os.urandom(1024 * 500)

    encrypted = public_rsa_key.encrypt(org_bytes)
    decrypted = private_rsa_key.decrypt(encrypted)

    assert org_bytes == decrypted
