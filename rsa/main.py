import os, json

from rsa_key import PrivateRsaKey, PublicRsaKey, RsaKey
from gcd import gcd
from gen_rsa_key import gen_rsa_key

from dataclasses import asdict

rsa_key = gen_rsa_key(512)

public_rsa_key = rsa_key.public_key()
private_rsa_key = rsa_key.private_key()


with open('public.rsa', 'w') as file:
    file.write(json.dumps(asdict(public_rsa_key), indent=2))

with open('private.rsa', 'w') as file:
    file.write(json.dumps(asdict(private_rsa_key), indent=2))

###############################################

with open('public.rsa', 'r') as file:
    public_rsa_key = PublicRsaKey(**json.loads(file.read()))

with open('private.rsa', 'r') as file:
    private_rsa_key = PrivateRsaKey(**json.loads(file.read()))


for i in range(100, 200):
    org_bytes = os.urandom(1024 * 500)

    encrypted = public_rsa_key.encrypt(org_bytes)
    decrypted = private_rsa_key.decrypt(encrypted)

    assert org_bytes == decrypted

    rsa_key = gen_rsa_key(i)
    public_rsa_key = rsa_key.public_key()
    private_rsa_key = rsa_key.private_key()
