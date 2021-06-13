from rsa.rsa_key import EncryptedBytes, encrypt_ECB, decrypt_ECB, encrypt_CBC, decrypt_CBC, encrypt_Lib
import click, json
import numpy as np
import cv2

from progressbar import progressbar
from rsa import MyRsaPrivateKey, MyRsaPublicKey
from png_decode import PNG_HEADER, decode

@click.group()
def cli():
    pass

@cli.command()
@click.option('--public-key', '-pk', default='public.rsa', help='File containing public RSA key')
@click.option('--input', '-i', help='Input image')
@click.option('--output', '-o', default='out.png', help='Output image')
@click.option('--method', '-m', default='ECB', help='Encryption method [EBC, CBC, LIB')
def encrypt(public_key, input, output, method):
    methods_dict = {
    "ECB": encrypt_ECB,
    "CBC": encrypt_CBC,
    "LIB": encrypt_Lib 
    }


    with open(public_key, 'r') as file:
        public_rsa_key = MyRsaPublicKey(**json.loads(file.read()))

    img = cv2.imread(input)
    h, w, px = img.shape

    
    encrypted_bytes = methods_dict[method](img.tobytes(), public_rsa_key)
    enc_img = np.frombuffer(encrypted_bytes.main_bytes, dtype='u1')
    enc_img = np.reshape(enc_img, [h, w, px])

    # save primary bytes
    cv2.imwrite(output, enc_img)

    with open(output, 'ab') as file:
        file.write(encrypted_bytes.rest_bytes)


@cli.command()
@click.option('--private-key', '-pk', default='private.rsa', help='File containing public RSA key')
@click.option('--input', '-i', help='Input image')
@click.option('--output', '-o', default='out.png', help='Output image')
@click.option('--method', '-m', default='ECB', help='Encryption method [EBC, CBC, LIB')
def decrypt(private_key, input, output, method):
    methods_dict = {
    "ECB": decrypt_ECB,
    "CBC": decrypt_CBC,
    }
    
    with open(private_key, 'r') as file:
        private_rsa_key = MyRsaPrivateKey(**json.loads(file.read()))

    enc_bytes = EncryptedBytes()

    img = cv2.imread(input)
    h, w, px = img.shape

    enc_bytes.main_bytes = img.tobytes()

    with open(input, 'rb') as file:
        _ = decode(file)
        enc_bytes.rest_bytes = file.read()

    decoded_image = np.frombuffer(
        methods_dict[method](enc_bytes, private_rsa_key),
        dtype='u1')
    decoded_image = np.reshape(decoded_image, [h, w, px])

    cv2.imwrite(output, decoded_image)

@cli.command()
@click.option('--input', '-i', help='First image')
@click.option('--output', '-o', help='Second image')
def compare(input, output):
    input_image = cv2.imread(input)
    output_image = cv2.imread(output)
    if( input_image.shape == output_image.shape):
        if not (input_image ^ output_image).any():
            print("IMAGES ARE THE SAME")
        else:
            print("IMAGES ARE NOT THE SAME (bytes)")
    else:
        print("IMAGES ARE NOT THE SAME (size)")


if __name__ == '__main__':
    cli()
