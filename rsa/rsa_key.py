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


@dataclass(frozen=True)
class PublicRsaKey:
    e: int
    n: int

    def encrypt(self, b: bytes):
        max_length_bytes = int(self.n.bit_length() / 8)
        bytes_to_save = int(math.ceil(self.n.bit_length() / 8))
        result = bytes()

        range_to_encrypt = len(b) - (len(b) % max_length_bytes)

        for offset in progressbar.progressbar(range(0, range_to_encrypt, max_length_bytes)):
            to_encrypt = int.from_bytes(b[offset:offset+max_length_bytes], 'little')
            encrypted = pow(to_encrypt, self.e, self.n)
            result += encrypted.to_bytes(bytes_to_save, byteorder='little')

        result += b[range_to_encrypt:]

        return result


@dataclass(frozen=True)
class PrivateRsaKey:
    d: int
    n: int

    def decrypt(self, b: bytes):
        max_length_bytes = int(self.n.bit_length() / 8)
        bytes_to_save = int(math.ceil(self.n.bit_length() / 8))
        result = bytes()

        encrypted_range = len(b) - (len(b) % bytes_to_save)

        for offset in progressbar.progressbar(range(0, encrypted_range, bytes_to_save)):
            to_decrypt = int.from_bytes(b[offset:offset+bytes_to_save], 'little')
            decrypted = pow(to_decrypt, self.d, self.n)
            result += decrypted.to_bytes(max_length_bytes, byteorder='little')

        result += b[encrypted_range:]

        return result
