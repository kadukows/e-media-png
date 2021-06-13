from dataclasses import dataclass
from werkzeug.utils import cached_property
import progressbar, math

from Crypto.Cipher import PKCS1_OAEP
from Cryptodome import Random
from Cryptodome.PublicKey import RSA
from Crypto.Hash import SHA

import Cryptodome as crypto
import random
import numpy as np
import copy


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

def encrypt_CBC(b: bytes, public_key: RsaPublicKey) -> EncryptedBytes:
    # size of input block in bytes
    decrypted_block_size = get_decrypted_block_size(public_key.bit_length())
    # size of output block in bytes
    encrypted_block_size = get_encrypted_block_size(public_key.bit_length())
    # range to encrypt with normal input_block size
    last_block_size = len(b) % decrypted_block_size
    range_to_encrypt = len(b) - last_block_size

    result = EncryptedBytes()
    
    
    initialization_vector = random.getrandbits(decrypted_block_size * 8)
    previous_vector =  initialization_vector.to_bytes(decrypted_block_size, 'little')

    for offset in progressbar.progressbar(range(0, range_to_encrypt, decrypted_block_size)):
        bytes_to_encrypt = copy.copy(b[offset:offset + decrypted_block_size])
        xor_bytes_to_encrypt = bytes(bytes_to_xor ^ vector for (bytes_to_xor, vector) in zip(bytes_to_encrypt, previous_vector[0:len(bytes_to_encrypt)]))
        encrypted = public_key.encrypt(xor_bytes_to_encrypt)
        previous_vector = encrypted

        # save the same size to main bytes
        result.main_bytes += encrypted[:decrypted_block_size]
        # save rest to other var
        result.rest_bytes += encrypted[decrypted_block_size:]


    #TODO Why is this 0 length
    last_bytes_to_encrypt = b[range_to_encrypt:]
    print(len(last_bytes_to_encrypt))
    xor_bytes_to_encrypt = bytes(b ^ vector for (b, vector) in zip(last_bytes_to_encrypt, previous_vector[0:len(last_bytes_to_encrypt)]))
    last_encrypted = public_key.encrypt(b[range_to_encrypt:])
    
    result.main_bytes += last_encrypted[:last_block_size]
    result.rest_bytes += last_encrypted[last_block_size:]

    # save size of lastblock as last 4 bytes
    result.rest_bytes += last_block_size.to_bytes(4, byteorder='little')

    return result

def decrypt_CBC(enc_bytes: EncryptedBytes, private_key: RsaPrivateKey) -> bytes:
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


    initialization_vector = random.getrandbits(encrypted_block_size * 8)
    previous_vector =  initialization_vector.to_bytes(encrypted_block_size * 8, 'little')

    for main_bytes_offset in progressbar.progressbar(range(0, range_to_decrypt, decrypted_block_size)):
        to_decrypt_main = enc_bytes.main_bytes[main_bytes_offset:main_bytes_offset + decrypted_block_size]
        to_decrypt_rest = enc_bytes.rest_bytes[rest_bytes_offset:rest_bytes_offset + diff]
        to_decrypt_bytes = to_decrypt_main + to_decrypt_rest

        decrypted = private_key.decrypt(to_decrypt_bytes)
        xor_bytes_decrypted = bytes(b ^ vector for (b, vector) in zip(decrypted, previous_vector[0:len(to_decrypt_bytes)]))
        previous_vector = to_decrypt_bytes

        result += xor_bytes_decrypted
        rest_bytes_offset += diff

    
    #TODO Is this correct?
    last_to_decrypt_main_part = enc_bytes.main_bytes[main_bytes_offset:main_bytes_offset + last_block_size]
    last_to_decrypt_rest_part = enc_bytes.rest_bytes[rest_bytes_offset:rest_bytes_offset + encrypted_block_size - last_block_size]
    last_to_decrypt_bytes = last_to_decrypt_main_part + last_to_decrypt_rest_part
    
    print(len(last_to_decrypt_bytes))
    last_decrypted = int.from_bytes(private_key.decrypt(last_to_decrypt_bytes), byteorder='little').to_bytes(last_block_size, byteorder='little')
    xor_bytes_decrypted = bytes(b ^ vector for (b, vector) in zip(last_decrypted, previous_vector[0:len(last_to_decrypt_bytes)]))


    result += last_decrypted
    
    return result

def encrypt_Lib(b: bytes, public_key: RsaPublicKey) -> EncryptedBytes:
    key = RSA.construct((public_key.n , public_key.e))
    cipher = PKCS1_OAEP.new(key)

    # size of input block in bytes
    #decrypted_block_size = (public_key.bit_length() - 1) // 32
    decrypted_block_size = 15

    # size of output block in bytes
    #encrypted_block_size = int(math.ceil(public_key.bit_length() / 32))
    encrypted_block_size = 16

    # range to encrypt with normal input_block size
    last_block_size = len(b) % decrypted_block_size
    range_to_encrypt = len(b) - last_block_size

    result = EncryptedBytes()

    for offset in progressbar.progressbar(range(0, range_to_encrypt, decrypted_block_size)):
        encrypted = cipher.encrypt(b[offset:offset + decrypted_block_size])

        # save the same size to main bytes
        result.main_bytes += encrypted[:decrypted_block_size]
        # save rest to other var
        result.rest_bytes += encrypted[decrypted_block_size:]


    last_encrypted = public_key.encrypt(b[range_to_encrypt:])
    result.main_bytes += last_encrypted[:last_block_size]
    result.rest_bytes += last_encrypted[last_block_size:]

    # save size of lastblock as last 4 bytes
    result.rest_bytes += last_block_size.to_bytes(4, byteorder='little')
    return result

#FIXME
def decrypt_Lib(enc_bytes: EncryptedBytes, private_key: RsaPrivateKey) -> bytes:
    key = RSA.construct((private_key.n , private_key.d))
    cipher = PKCS1_OAEP.new(key)

    # size of input block in bytes
    #decrypted_block_size = (public_key.bit_length() - 1) // 32
    decrypted_block_size = 15

    # size of output block in bytes
    #encrypted_block_size = int(math.ceil(public_key.bit_length() / 32))
    encrypted_block_size = 16

    
    
    last_block_size = int.from_bytes(enc_bytes.rest_bytes[-4:], 'little')
    range_to_decrypt = len(enc_bytes.main_bytes) - last_block_size

    #assert range_to_decrypt % decrypted_block_size == 0

    result = bytes()
    rest_bytes_offset = 0
    diff = encrypted_block_size - decrypted_block_size
    for main_bytes_offset in progressbar.progressbar(range(0, range_to_decrypt, decrypted_block_size)):
        to_decrypt_main = enc_bytes.main_bytes[main_bytes_offset:main_bytes_offset + decrypted_block_size]
        to_decrypt_rest = enc_bytes.rest_bytes[rest_bytes_offset:rest_bytes_offset + diff]
        print(len(to_decrypt_main + to_decrypt_rest))
        decrypted = cipher.decrypt(to_decrypt_main + to_decrypt_rest)

        result += decrypted
        rest_bytes_offset += diff

    last_to_decrypt_main_part = enc_bytes.main_bytes[main_bytes_offset:main_bytes_offset + last_block_size]
    last_to_decrypt_rest_part = enc_bytes.rest_bytes[rest_bytes_offset:rest_bytes_offset + encrypted_block_size - last_block_size]
    last_to_decrypted = int.from_bytes(cipher.decrypt(last_to_decrypt_main_part + last_to_decrypt_rest_part), byteorder='little').to_bytes(last_block_size, byteorder='little')

    result += last_to_decrypted

    return result



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
        result.rest_bytes += encrypted[decrypted_block_size:]


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
    last_to_decrypt_rest_part = enc_bytes.rest_bytes[rest_bytes_offset:rest_bytes_offset + encrypted_block_size - last_block_size]
    last_to_decrypted = int.from_bytes(private_key.decrypt(last_to_decrypt_main_part + last_to_decrypt_rest_part), byteorder='little').to_bytes(last_block_size, byteorder='little')

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
        #self.encrypted_block_size = get_encrypted_block_size(n.bit_length())
        self.encrypted_block_size = 48

    def bit_length(self) -> int:
        return self.n.bit_length()

    def encrypt(self, b: bytes) -> bytes:
        assert len(b) < self.n.bit_length()
        key = RSA.construct((self.n , self.e))
        cipher = PKCS1_v1_5.new(key)

        encrypted = cipher.encrypt(b[:self.encrypted_block_size])
        encrypted += cipher.encrypt(b[self.encrypted_block_size:])

        '''
        encrypted = bytes()
        for i in range(0, len(b), self.encrypted_block_size ):
            bytes_chunk_to_encrypt = b[i: i + self.encrypted_block_size ]
            encrypted += cipher.encrypt(bytes_chunk_to_encrypt)
        '''

        return encrypted



class LibRsaPrivateKey(RsaPrivateKey):
    def __init__(self, d: int, n: int):
        self.d = d
        self.n = n
        self.decrypted_block_size = 47

    def bit_length(self) -> int:
        return self.n.bit_length()

    def decrypt(self, b: bytes) -> bytes:
        key = RSA.construct((self.n , self.d))

        sentinel = Random.new().read(256)
        cipher = PKCS1_v1_5.new(key)
        decrypted = cipher.decrypt(b[:self.decrypted_block_size],sentinel)
        decrypted += cipher.decrypt(b[self.decrypted_block_size:],sentinel)

        return decrypted
