from functools import cached_property

class SieveSingleton:
    _SIEVE_LENGTH = 50000

    @cached_property
    def primes(self):
        sieve = [True] * SieveSingleton._SIEVE_LENGTH
        sieve[0] = False
        sieve[1] = False

        cur_prime = 0
        while (cur_prime := next((number + cur_prime for number, is_prime in enumerate(sieve[cur_prime:]) if is_prime), None)) is not None:
            for i in range(2, int(SieveSingleton._SIEVE_LENGTH / cur_prime)):
                sieve[i * cur_prime] = False

            cur_prime += 1

        return tuple(number for number, is_prime in enumerate(sieve) if is_prime and number > 1000)

sieve_singleton = SieveSingleton()
