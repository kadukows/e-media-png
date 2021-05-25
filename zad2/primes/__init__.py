_SIEVE_LENGTH = 10000 * 3
_SIEVE = [True] * _SIEVE_LENGTH

_SIEVE[0] = False
_SIEVE[1] = False

_cur_prime = 0
while (_cur_prime := next((number + _cur_prime for number, is_prime in enumerate(_SIEVE[_cur_prime:]) if is_prime), None)) is not None:
    i = 2
    while _cur_prime * i < len(_SIEVE):
        _SIEVE[_cur_prime * i] = False
        i += 1
    _cur_prime += 1 # skip to the next

_PRIMES = tuple(number for number, is_prime in enumerate(_SIEVE) if is_prime)
del _SIEVE_LENGTH, _SIEVE


from .gen_prime import gen_prime
