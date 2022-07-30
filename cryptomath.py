# --- Mathematical methods used in elliptic curve cryptography --- #

def legendre_symbol(n: int, p: int) -> int:
    '''
    We calculate n^(p-1)/2 (mod p). The result will either be 0, 1 or p-1.
    If it's p-1 we return -1 otherwise we return the value
    '''
    flt = pow(n, (p - 1) // 2, p)
    if flt == p - 1:
        return -1
    return flt


def is_quadratic_residue(n: int, p: int) -> bool:
    '''
    Returns True if (n|p) != -1
    '''
    if legendre_symbol(n, p) == -1:
        return False
    return True


def tonelli_shanks(n: int, p: int):
    '''
    If n is a quadratic residue mod p, then we return an integer r such that r^2 = n (mod p).
    '''

    # Verify n is a quadratic residue
    if legendre_symbol(n, p) == -1:
        return None

    # Trivial case
    if n % p == 0:
        return 0

    # p = 3 (mod 4) case
    if p % 4 == 3:
        return pow(n, (p + 1) // 4, p)

    ###--- General Case ---###
    # 1) Divide p-1 into its even and odd components by p-1 = 2^s * Q, where Q is odd and s >=1
    Q = p - 1
    s = 0
    while Q % 2 == 0:
        s += 1
        Q //= 2

    # 2) Find a quadratic non residue
    z = 2
    while legendre_symbol(z, p) != -1:
        z += 1

    # 3) Configure initial variables
    M = s
    c = pow(z, Q, p)
    t = pow(n, Q, p)
    R = pow(n, (Q + 1) // 2, p)

    # 4) Repeat until t == 1
    while t != 1:

        # First find the least integer i such that t^(2^i) = 1 (mod p)
        i = 0
        factor = t
        while factor != 1:
            i += 1
            factor = (factor * factor) % p

        # Reassign variables
        exp = 2 ** (M - i - 1)
        b = pow(c, exp, p)
        M = i
        c = (b * b) % p
        t = (t * c) % p
        R = (R * b) % p

    return R
