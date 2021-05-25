from dataclasses import dataclass
from functools import cached_property

@dataclass(frozen=True)
class RsaKey:
    p: int
    q: int
    e: int
    d: int

    @cached_property
    def n(self):
        return self.p * self.q

    @cached_property
    def public_key(self):
        return {
            'e': self.e,
            'n': self.n
        }

    @cached_property
    def private_key(self):
        return {
            'd': self.d,
            'n': self.n
        }
