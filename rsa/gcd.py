from .int_ptr import IntPtr

def gcd(a: int, b: int) -> int:
    if a == 0:
        return b
    elif b == 0:
        return a

    r_b = a % b
    return gcd(b, r_b)

def extended_euclid(a: int, b: int, x: IntPtr, y: IntPtr) -> int:
    if a == 0:
        x.val = 0
        y.val = 1
        return b

    x1 = IntPtr(val=0)
    y1 = IntPtr(val=0)
    gcd = extended_euclid(b % a, a, x1, y1)

    x.val = y1.val - int(b/a) * x1.val
    y.val = x1.val

    return gcd

def modInverse(a: int, m: int):
    x = IntPtr(val=0)
    y = IntPtr(val=0)
    assert extended_euclid(a, m, x, y) == 1

    # handle negative value
    return (x.val % m + m) % m
