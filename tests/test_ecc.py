# ---IMPORTS---#

from elliptic_curve import CurveFactory

# ---CONSTANTS---#

A = 0
B = 7
P = pow(2, 256) - pow(2, 32) - pow(2, 9) - pow(2, 8) - pow(2, 7) - pow(2, 6) - pow(2, 4) - 1
ORDER = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141
GENERATOR_X = 0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798
GENERATOR_Y = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8


# ---TESTS---#


def test_factory():
    '''
    We verify that all fail conditions of the CurveFactory will actually fail as expected
    '''
    factory = CurveFactory()

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
