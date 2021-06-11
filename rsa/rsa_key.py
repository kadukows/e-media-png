from dataclasses import dataclass
from functools import cached_property
import progressbar, math

class RsaPublicKey:
    def encrypt(self, b: bytes) -> bytes:
        raise NotImplementedError()

    def bit_length(self) -> int:
        ''' Returns bit length of a modulus. '''
        raise NotImplementedError()


class RsaPrivateKey:
    def decrypt(self, b: bytes) -> bytes:
        raise NotImplementedError()

    def bit_length(self) -> int:
        ''' Returns bit length of a modulus. '''
        raise NotImplementedError()



@dataclass(frozen=True)
class RsaKey:
    p: int
    q: int
    e: int
    d: int

    @cached_property
    def n(self):
        return self.p * self.q

    def public_key(self):
        return MyRsaPublicKey(e=self.e, n=self.n)

    def private_key(self):
        return MyRsaPrivateKey(d=self.d, n=self.n)




def get_decrypted_block_size(bit_length) -> int:
    return (bit_length - 1) // 8

def get_encrypted_block_size(bit_length) -> int:
    return int(math.ceil(bit_length / 8))



@dataclass
class EncryptedBytes:
    main_bytes: bytes = bytes()
    rest_bytes: bytes = bytes()



def encrypt_ECB(b: bytes, public_key: RsaPublicKey) -> EncryptedBytes:
    # size of input block in bytes
    decrypted_block_size = get_decrypted_block_size(public_key.bit_length())

    # size of output block in bytes
    encrypted_block_size = get_encrypted_block_size(public_key.bit_length())

    # range to encrypt with normal input_block size
    last_block_size = len(b) % decrypted_block_size
    range_to_encrypt = len(b) - last_block_size

    result = EncryptedBytes()

    for offset in progressbar.progressbar(range(0, range_to_encrypt, decrypted_block_size)):
        encrypted = public_key.encrypt(b[offset:offset + decrypted_block_size])

        # save the same size to main bytes
        result.main_bytes += encrypted[:decrypted_block_size]
        # save rest to other var
        result.rest_bytes += encrypted[encrypted_block_size:]


    last_encrypted = public_key.encrypt(b[range_to_encrypt:])
    result.main_bytes += last_encrypted[:last_block_size]
    result.rest_bytes += last_encrypted[last_block_size:]

    # save size of lastblock as last 4 bytes
    result.rest_bytes += last_block_size.to_bytes(4, byteorder='little')

    return result




def decrypt_ECB(enc_bytes: EncryptedBytes, private_key: RsaPrivateKey) -> bytes:
    # size of input block in bytes
    decrypted_block_size = get_decrypted_block_size(private_key.bit_length())

    # size of output block in bytes
    encrypted_block_size = get_encrypted_block_size(private_key.bit_length())

    last_block_size = int.from_bytes(enc_bytes.rest_bytes[-4:], 'little')
    range_to_decrypt = len(enc_bytes.main_bytes) - last_block_size

    assert range_to_decrypt % decrypted_block_size == 0

    result = bytes()
    rest_bytes_offset = 0
    diff = encrypted_block_size - decrypted_block_size
    for main_bytes_offset in progressbar.progressbar(range(0, range_to_decrypt, decrypted_block_size)):
        to_decrypt_main = enc_bytes.main_bytes[main_bytes_offset:main_bytes_offset + decrypted_block_size]
        to_decrypt_rest = enc_bytes.rest_bytes[rest_bytes_offset:rest_bytes_offset + diff]
        decrypted = private_key.decrypt(to_decrypt_main + to_decrypt_rest)

        result += decrypted
        rest_bytes_offset += diff

    last_to_decrypt_main_part = enc_bytes.main_bytes[main_bytes_offset:main_bytes_offset + last_block_size]
    last_to_decrypt_rest_part = enc_bytes.rest_bytes[rest_bytes_offset:encrypted_block_size - last_block_size]
    last_to_decrypted = private_key.decrypt(last_to_decrypt_main_part + last_to_decrypt_rest_part)

    result += last_to_decrypted

    return result





class MyRsaPublicKey(RsaPublicKey):
    def __init__(self, e: int, n: int):
        self.e = e
        self.n = n
        self.encrypted_block_size = get_encrypted_block_size(n.bit_length())

    def bit_length(self) -> int:
        return self.n.bit_length()

    def encrypt(self, b: bytes) -> bytes:
        _int = int.from_bytes(b, byteorder='little')
        assert _int < self.n
        return pow(_int, self.e, self.n).to_bytes(self.encrypted_block_size, byteorder='little')



class MyRsaPrivateKey(RsaPrivateKey):
    def __init__(self, d: int, n: int):
        self.d = d
        self.n = n
        self.decrypted_block_size = get_decrypted_block_size(n.bit_length())

    def bit_length(self) -> int:
        return self.n.bit_length()

    def decrypt(self, b: bytes) -> bytes:
        _int = int.from_bytes(b, byteorder='little')
        assert _int < self.n
        return pow(_int, self.d, self.n).to_bytes(self.decrypted_block_size, byteorder='little')

class LibRsaPublicKey(RsaPublicKey):
    def __init__(self, e: int, n: int):
        self.e = e
        self.n = n
        self.encrypted_block_size = get_encrypted_block_size(n.bit_length())

    def bit_length(self) -> int:
        return self.n.bit_length()

    def encrypt(self, b: bytes) -> bytes:
        key = RSA.construct((self.n , self.e))
        cipher = PKCS1_OAEP.new(key)
        encyrpted = cipher.encrypt(b)
        return encyrpted



class LibRsaPrivateKey(RsaPrivateKey):
    def __init__(self, d: int, n: int):
        self.d = d
        self.n = n
        self.decrypted_block_size = get_decrypted_block_size(n.bit_length())

    def bit_length(self) -> int:
        return self.n.bit_length()

    def decrypt(self, b: bytes) -> bytes:
        _int = int.from_bytes(b, byteorder='little')
        assert _int < self.n
        return pow(_int, self.d, self.n).to_bytes(self.decrypted_block_size, byteorder='little')
