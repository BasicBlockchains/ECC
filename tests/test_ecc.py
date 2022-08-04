# ---IMPORTS---#
import random

from primefac import isprime

from src.basicblockchains_ecc import elliptic_curve as EC

# ---CONSTANTS---#

P = pow(2, 256) - pow(2, 32) - pow(2, 9) - pow(2, 8) - pow(2, 7) - pow(2, 6) - pow(2, 4) - 1  # sepc256k1
ORDER = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141  # sepc256k1

COEFFICIENT_UPPER_BOUND = 10
PRIME_UPPER_BOUND = pow(2, 13) - 1  # 5th Mersenne Prime

curve_list = [
    EC.secp192k1(),
    EC.secp192r1(),
    EC.secp224k1(),
    EC.secp224r1(),
    EC.secp256k1(),
    EC.secp256r1(),
    EC.secp384r1(),
    EC.secp521r1()
]

# ---TESTS---#

def test_curve_functions():
    '''
    We deploy a curve with a known prime order and verify that a random point (not point at infinity) will generate all the elements.
    '''
    # List of primes
    prime_list = create_odd_prime_list()

    # Create curve loop
    factory = EC.CurveFactory()
    curve = None
    while curve is None:
        a = random.choice([x for x in range(COEFFICIENT_UPPER_BOUND)])
        b = random.choice([x for x in range(COEFFICIENT_UPPER_BOUND)])
        random_prime = random.choice(prime_list)
        curve = factory.create_curve(a, b, random_prime)  # Factory will return curve with prime order

    assert isprime(curve.order)
    assert curve.generator

    curve_values = []
    for x in range(1, curve.order):
        curve_values.append(curve.scalar_multiplication(x, curve.generator))
    unique_values = set(curve_values)

    assert len(unique_values) == curve.order - 1  # Exluding point at infinity
    assert len(unique_values) == len(curve_values)  # All points are uniquely generated by the generator


def test_factory():
    '''
    We verify that all fail conditions of the CurveFactory will actually fail as expected
    '''
    factory = EC.CurveFactory()

    # 1 - p is not prime
    c1 = factory.create_curve(a=0, b=7, p=15)
    assert c1 is None

    # 2 - curve is singular
    c2 = factory.create_curve(a=0, b=0, p=41)
    assert c2 is None

    # 3 - order given is not prime
    c3 = factory.create_curve(a=0, b=7, p=41, order=42)
    assert c3 is None

    # 4 - order not given for p large
    c4 = factory.create_curve(a=0, b=7, p=P)
    assert c4 is None

    # 5 - order not given and is not prime
    c5 = factory.create_curve(a=0, b=7, p=41)
    assert c4 is None

    # 6 - generator not given for large prime - should yield random point
    c6 = factory.create_curve(a=0, b=7, p=P, order=ORDER)
    assert c6.generator is not None
    assert c6.is_point_on_curve(c6.generator)

    # 7 - generator given but not on curve
    c7 = factory.create_curve(a=0, b=7, p=43, generator=(1, 1))
    assert c7.generator != (1, 1)
    assert c7.is_point_on_curve(c7.generator)


def test_secp_curves():


    for curve in curve_list:
        assert isprime(curve.p)  # Verify prime
        assert isprime(curve.order)  # Verify prime ordr
        gx, gy = curve.generator
        y = curve.find_y_from_x(gx)
        if y % 2 != gy % 2:
            y = curve.p - y
        assert y == gy  # Verify we recover correct y from given x
        assert curve.scalar_multiplication(curve.order, curve.generator) is None  # Verify order

        # Check that any random point is a generator
        random_point = curve.random_point()
        assert curve.scalar_multiplication(curve.order, random_point) is None

        # Check the additive inverses of a random point
        p1, p2 = random_point
        i1, i2 = curve.scalar_multiplication(curve.order - 1, random_point)
        assert p1 == i1
        assert curve.p - p2 == i2
        assert curve.p - i2 == p2


def test_point_compression():
    for curve in curve_list:
        random_point = curve.random_point()
        compressed_point = curve.compress_point(random_point)
        decompressed_point = curve.decompress_point(compressed_point)
        assert decompressed_point == random_point


# --- HELPER FUNCTIONS --- #

def create_odd_prime_list() -> list:
    '''
    We return a list of all primes up to the PRIME_UPPER_BOUND.
    '''
    prime_list = []
    x = 3
    while x <= PRIME_UPPER_BOUND:
        if isprime(x):
            prime_list.append(x)
        x += 1
    return prime_list
