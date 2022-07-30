# --- IMPORTS --- #
import secrets

import primefac

from cryptomath import is_quadratic_residue, tonelli_shanks


# --- CLASSES --- #

class CurveFactory:
    # --- CONSTANT --- #
    MAX_PRIME = pow(2, 19) - 1  # Mersenne Prime

    # --- FACTORY -- #
    def create_curve(self, a: int, b: int, p: int, order=None, generator=None):
        # Verify prime p
        if not primefac.isprime(p):
            return None

        # Verify curve non-singular
        disc = (-16 * (4 * pow(a, 3) + 27 * pow(b, 3))) % p
        if disc == 0:
            return None

        # If order is given, make sure it's prime
        if order is not None:
            if not primefac.isprime(order):
                return None

        # Verify order given for large prime
        if p > self.MAX_PRIME and order is None:
            return None

        # Get non-singular curve over F_p, with prime order for p >= MAX_PRIME
        curve = EllipticCurve(a=a, b=b, p=p, order=order, generator=generator)

        # Get order if p < MAX_PRIME
        if p <= self.MAX_PRIME:
            temp_order = curve.get_order()

            # Verify order if it exists - if not, replace with calculated order
            if order is not None and order != temp_order:
                curve = EllipticCurve(a=a, b=b, p=p, order=temp_order, generator=generator)

            # Return None if order isn't prime
            if not primefac.isprime(temp_order):
                return None

            # Return None if generator not given
            if curve.generator is None:
                return None

        return curve


class EllipticCurve:

    def __init__(self, a: int, b: int, p: int, order=None, generator=None):
        '''
        We instantiate an elliptic curve E of the form

            y^2 = x^3 + ax + b (mod p).

        We let E(F_p) denote the corresponding cyclic abelian group, comprised of the rational points of E and the
        point at infinity. The order variable refers to the order of this group. As the group is cyclic,
        it will contain a generator point, which can be specified during instantiation.

        '''
        # Get curve values
        self.a = a
        self.b = b
        self.p = p

        # Get order for small prime
        if self.p <= CurveFactory.MAX_PRIME and order is None:
            self.order = self.get_order()
        else:
            self.order = order

        # Check if generator is on the curve
        if generator is not None and not self.is_point_on_curve(generator):
            generator = None

        # Get generator
        self.generator = generator
        if generator is None:
            self.generator = self.random_point()

    # --- Right Hand Side --- #

    def x_terms(self, x):
        return pow(x, 3) + self.a * x + self.b

    # --- Points on curve --- #

    def random_point(self) -> tuple:
        '''

        '''
        x = secrets.randbelow(self.p - 1)
        while not self.is_x_on_curve(x):
            x += 1
            if x >= self.p - 1:  # If x gets too big we choose another x
                x = secrets.randbelow(self.p - 1)

        y = self.find_y_from_x(x)
        point = (x, y)
        return point

    def is_point_on_curve(self, point: tuple) -> bool:
        '''

        '''
        # Point at infinity case first
        if point is None:
            return True

        # Return True if y^2 = x^3 + ax +b (mod p) and False otherwise
        x, y = point
        return (self.x_terms(x) - pow(y, 2)) % self.p == 0

    def is_x_on_curve(self, x: int) -> bool:
        '''
        A residue x is on the curve E iff x^3 + ax + b is a quadratic residue modulo p.
        We use the is_quadratic_residue method from cryptomath
        '''

        return is_quadratic_residue(self.x_terms(x), self.p)

    def find_y_from_x(self, x: int):
        '''
        Using tonelli shanks, we return y such that E(x,y) = 0, if x is on the curve.
        Note that if (x,y) is a point then (x,p-y) will be a point as well.
        '''

        # Verify x is on curve
        try:
            assert self.is_x_on_curve(x)
        except AssertionError:
            return None

        # Find the two possible y values
        y = tonelli_shanks(self.x_terms(x), self.p)
        neg_y = -y % self.p

        # Check y values
        try:
            assert self.is_point_on_curve((x, y))
            assert self.add_points((x, y), (x, neg_y)) is None
        except AssertionError:
            return None

        # Return y
        return y

    # --- Group operations --- #

    def add_points(self, point1: tuple, point2: tuple):
        '''
        Adding points using the elliptic curve addition rules.
        '''

        # Verify points exist
        try:
            assert self.is_point_on_curve(point1)
            assert self.is_point_on_curve(point2)
        except AssertionError:
            return None

        # Point at infinity cases
        if point1 is None:
            return point2
        if point2 is None:
            return point1

        # Get coordinates
        x1, y1 = point1
        x2, y2 = point2

        # Get slope if it exists
        if x1 == x2:
            if y1 != y2:  # Points are inverses
                return None
            elif y1 == 0:  # Point is its own inverse when lying on the x axis
                return None
            else:  # Points are the same
                m = ((3 * x1 * x1 + self.a) * pow(2 * y1, -1, self.p)) % self.p
        else:  # Points are distinct
            m = ((y2 - y1) * pow(x2 - x1, -1, self.p)) % self.p

        # Use the addition formulas
        x3 = (m * m - x1 - x2) % self.p
        y3 = (m * (x1 - x3) - y1) % self.p
        point = (x3, y3)

        # Verify result
        try:
            assert self.is_point_on_curve(point)
        except AssertionError:
            return None

        # Return sum of points
        return point

    def scalar_multiplication(self, n: int, point: tuple):
        '''
        We use the double-and-add algorithm to add a point P with itself n times.

        Algorithm:
        ---------
        Break n into a binary representation (big-endian).
        Then iterate over each bit in the representation as follows:
            1) If it's the first bit, ignore;
            2) double the previous result (starting with P)
            3) if the bit = 1, add a copy of P to the result.

        Ex: n = 26. Binary representation = 11010
            bit     | action        | result
            --------------------------------
            1       | ignore        | P
            1       | double/add    | 2P + P = 3P
            0       | double        | 6P
            1       | double/add    | 12P + P = 13P
            0       | double        | 26P
        '''
        # Retrieve order if it's None - only for small primes
        if self.order is None:
            self.order = self.get_order()

        # Point at infinity case
        if point is None:
            return None

        # Scalar multiple divides group order
        if n % self.order == 0:
            return None

        # Take residue of n modulo the group order
        n = n % self.order

        # Proceed with algorithm
        bitstring = bin(n)[2:]
        temp_point = point
        for x in range(1, len(bitstring)):
            temp_point = self.add_points(temp_point, temp_point)  # Double regardless of bit
            bit = int(bitstring[x:x + 1], 2)
            if bit == 1:
                temp_point = self.add_points(temp_point, point)  # Add to the doubling if bit == 1

        # Verify results
        try:
            assert self.is_point_on_curve(temp_point)
        except AssertionError:
            return None

        # Return point
        return temp_point

    def get_order(self):
        '''
        We naively calculate the order by iterating over all x in F_p. If x is on the curve we
        obtain y. If y is not zero, then we known (x,y) and (x,p-y) are two points on the curve. Otherwise, (x,
        0) is a point on the curve (on the x-axis). Hence, we sum up these values and add the point at infinity to
        return the order.

        NOTE: This should only be used for small primes.
        '''

        sum = 1  # Start with point of infinity
        for x in range(0, self.p):
            if self.is_x_on_curve(x):
                y = self.find_y_from_x(x)
                if y == 0:
                    sum += 1
                else:
                    sum += 2
        return sum

    # --- ECDSA --- #

    def generate_signature(self, private_key: int, hex_string: str):
        '''
        For a given private_key and hex_string, we generate a signature for this curve.


        Algorithm:
        ---------
        Let E denote the elliptic curve and let n denote the group order.
        We emphasize that n IS NOT necessarily equal to the characteristic p of F_p.
        Let t denote the private_key.

        1) Verify that n is prime - the signature will not work if we do not have prime group order.
        2) Let Z denote the integer value of the first n BITS of the hex_string.
        3) Select a random integer k in [1, n-1]. As n is prime, k will be invertible.
        4) Calculate the curve point (x,y) =  k * generator
        5) Compute r = x (mod n) and s = k^(-1)(Z + r * t) (mod n). If either r or s = 0, repeat from step 3.
        6) The signature is the pair (r, s)
        '''

        # 1) Let n denote the group order
        n = self.order

        # Return None if order not given or order isn't prime
        if n is None or not primefac.isprime(n):
            return None

        # 2) Take the first n bits of the hex string
        Z = int(bin(int(hex_string, 16))[2:2 + n], 2)

        # 3) Select a random integer k (Loop from here)
        signed = False
        sig = None
        while not signed:
            k = secrets.randbelow(n)

            # 4) Calculate curve point
            x, y = self.scalar_multiplication(k, self.generator)

            # 5) Compute r and s
            r = x % n
            s = (pow(k, -1, n) * (Z + r * private_key)) % n

            if r != 0 and s != 0:
                sig = (r, s)
                public_key = self.scalar_multiplication(private_key, self.generator)
                signed = self.verify_signature(signature=sig, hex_string=hex_string, public_key=public_key)

        # 6) Return the signature (r,s)
        return sig

    def verify_signature(self, signature: tuple, hex_string: str, public_key: tuple) -> bool:
        '''
        We verify that the given signature corresponds to the correct public_key for the given hex_string.

        Algorithm
        --------
        Let n denote the group order of the elliptic curve.

        1) Verify that n is prime and that (r,s) are integers in the interval [1,n-1]
        2) Let Z be the integer value of the first n BITS of the transaction hash
        3) Let u1 = Z * s^(-1) (mod n) and u2 = r * s^(-1) (mod n)
        4) Calculate the curve point (x,y) = (u1 * generator) + (u2 * public_key)
            (where * is scalar multiplication, and + is elliptic curve point addition mod p)
        5) If r = x (mod n), the signature is valid.
        '''

        # Get signature values
        (r, s) = signature

        # 1) Verify our values first
        n = self.order  # From the factory, we know that the order will be given.
        try:
            assert 1 <= r <= n - 1
            assert 1 <= s <= n - 1
            assert primefac.isprime(n)
        except AssertionError:
            return False

        # 2) Take the first n bits of the transaction hash
        Z = int(bin(int(hex_string, 16))[2:2 + n], 2)

        # 3) Calculate u1 and u2
        s_inv = pow(s, -1, n)
        u1 = (Z * s_inv) % n
        u2 = (r * s_inv) % n

        # 4) Calculate the point
        point = self.add_points(self.scalar_multiplication(u1, self.generator),
                                self.scalar_multiplication(u2, public_key))

        # 5) Return True/False based on x. Account for point at infinity.
        if point is None:
            return False
        x, y = point
        return r == x % n


# --- CRYPTO CURVE --- #


def secp256k1():
    # Constants
    a = 0
    b = 7
    p = pow(2, 256) - pow(2, 32) - pow(2, 9) - pow(2, 8) - pow(2, 7) - pow(2, 6) - pow(2, 4) - 1
    order = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141
    generator = (0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798,
                 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8)

    # Return curve object
    return EllipticCurve(a, b, p, order, generator)
