from dataclasses import dataclass
from functools import cached_property
import progressbar, math

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
        return PublicRsaKey(e=self.e, n=self.n)

    def private_key(self):
        return PrivateRsaKey(d=self.d, n=self.n)


def get_unencrytped_block_size(n) -> int:
    return (n.bit_length() - 1) // 8

def get_encrypted_block_size(n) -> int:
    return int(math.ceil(n.bit_length() / 8))

@dataclass
class EncryptedBytes:
    main_bytes: bytes = bytes()
    rest_bytes: bytes = bytes()


@dataclass(frozen=True)
class PublicRsaKey:
    e: int
    n: int

    def encrypt_better_ecb(self, b: bytes) -> EncryptedBytes:
        # size of input block in bytes
        input_block = (self.n.bit_length() - 1) // 8

        # size of output block in bytes
        output_block = int(math.ceil(self.n.bit_length() / 8))

        # range to encrypt with normal input_block size
        last_block_size = (len(b) % input_block)
        range_to_encrypt = len(b) - last_block_size

        result = EncryptedBytes()

        for offset in progressbar.progressbar(range(0, range_to_encrypt, input_block)):
            to_encrypt = int.from_bytes(b[offset:offset+input_block], 'little')
            encrypted = pow(to_encrypt, self.e, self.n).to_bytes(output_block, byteorder='little')
            # save the same size to main bytes
            result.main_bytes += encrypted[:input_block]
            # save rest to other var
            result.rest_bytes += encrypted[input_block:]

        last_to_encrypt = int.from_bytes(b[range_to_encrypt:], 'little')
        last_encrypted = pow(last_to_encrypt, self.e, self.n).to_bytes(output_block, byteorder='little')
        result.main_bytes += last_encrypted[:(len(b) % input_block)]
        result.rest_bytes += last_encrypted[(len(b) % input_block):]
        # save size of lastblock as last 4 bytes
        result.rest_bytes += last_block_size.to_bytes(4, byteorder='little')

        return result

@dataclass(frozen=True)
class PrivateRsaKey:
    d: int
    n: int

    def decrypt_better_ecb(self, enc_bytes: EncryptedBytes) -> bytes:
        # size of input block in bytes
        encrypted_block_size = get_encrypted_block_size(self.n)

        # size of output block in bytes
        decrypted_block_size = get_unencrytped_block_size(self.n)

        last_block_size = int.from_bytes(enc_bytes.rest_bytes[-4:], 'little')
        range_to_decrypt = len(enc_bytes.main_bytes) - last_block_size

        assert range_to_decrypt % decrypted_block_size == 0

        result = bytes()
        rest_bytes_offset = 0
        diff = encrypted_block_size - decrypted_block_size
        for main_bytes_offset in progressbar.progressbar(range(0, range_to_decrypt, decrypted_block_size)):
            to_decrypt_main = enc_bytes.main_bytes[main_bytes_offset:main_bytes_offset + decrypted_block_size]
            to_decrypt_rest = enc_bytes.rest_bytes[rest_bytes_offset:rest_bytes_offset + diff]

            decrypted_int = int.from_bytes(to_decrypt_main + to_decrypt_rest, byteorder='little')
            decrypted = pow(decrypted_int, self.d, self.n).to_bytes(decrypted_block_size, byteorder='little')

            result += decrypted
            rest_bytes_offset += diff

        last_to_decrypt_main_part = enc_bytes.main_bytes[main_bytes_offset:main_bytes_offset + last_block_size]
        last_to_decrypt_rest_part = enc_bytes.rest_bytes[rest_bytes_offset:encrypted_block_size - last_block_size]
        last_to_decrypt_int = int.from_bytes(last_to_decrypt_main_part + last_to_decrypt_rest_part, byteorder='little')
        last_to_decrypted = pow(last_to_decrypt_int, self.d, self.n).to_bytes(last_block_size, byteorder='little')

        result += last_to_decrypted

        return result
