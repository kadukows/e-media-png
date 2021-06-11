from rsa.gen_rsa_key import gen_rsa_key
import sys, click, json
import numpy as np

from progressbar import progressbar
from rsa import PrivateRsaKey, PublicRsaKey
from png_decode import PNG_HEADER, decode

@click.group()
def cli():
    pass

@cli.command()
@click.option('--public-key', '-pk', default='public.rsa', help='File containing public RSA key')
@click.option('--input', '-i', help='Input image')
@click.option('--output', '-o', default='out.png', help='Output image')
def encrypt(public_key, input, output):
    with open(public_key, 'r') as file:
        public_rsa_key = PublicRsaKey(**json.loads(file.read()))

    with open(input, 'rb') as file:
        chunks = decode(file)
        ihdr_chunk = next(chunk for chunk in chunks if chunk.chunk_name == 'IHDR')
        print(ihdr_chunk)

    idat_chunks = (chunk for chunk in chunks if chunk.chunk_name == 'IDAT')
    for chunk in idat_chunks:
        print('Encrypting IDAT chunk')
        chunk.data = np.frombuffer(public_rsa_key.encrypt(chunk.data.tobytes()), dtype=np.uint8)

    with open(output, 'wb') as file:
        file.write(PNG_HEADER)
        print('Writing encrypted image')
        for chunk in progressbar(chunks):
            file.write(chunk.to_bytes())


@cli.command()
@click.option('--private-key', '-pk', default='private.rsa', help='File containing public RSA key')
@click.option('--input', '-i', help='Input image')
@click.option('--output', '-o', default='out.png', help='Output image')
def decrypt(private_key, input, output):
    with open(private_key, 'r') as file:
        private_rsa_key = PrivateRsaKey(**json.loads(file.read()))

    with open(input, 'rb') as file:
        chunks = decode(file)

    idat_chunks = (chunk for chunk in chunks if chunk.chunk_name == 'IDAT')
    for chunk in idat_chunks:
        print('Decrypting IDAT chunk')
        chunk.data = np.frombuffer(private_rsa_key.decrypt(chunk.data.tobytes()), dtype=np.uint8)

    with open(output, 'wb') as file:
        file.write(PNG_HEADER)
        print('Writing decrypted image')
        for chunk in progressbar(chunks):
            file.write(chunk.to_bytes())

@cli.command()
def gen_rsa():
    rsa = gen_rsa_key(512)


if __name__ == '__main__':
    cli()
