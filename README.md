# Basic Blockchains ECC

BasicBlockchains_ECC is a Python library for elliptic curve cryptography. It has all NIST secp curves available by
default and is suitable for use in a cryptographically secure blockchain.

## Installation

```pip install basicblockchains-ecc```

## General Usage

The EllipticCurve class can be instantiated using coefficients a and b and an odd prime p. As well, we have the
option to include the group order and a generator point. We use the factory method to
generate curves that can be used for ECC and the ECDSA; this is the CurveFactory class. This class will verify that

- p is prime
- the curve is __non_singular__
- if the order is given, it's prime
- if p > MAX_PRIME, then the order is not None
- if p <= MAX_PRIME, then the calculated order is prime
- if p <= MAX_PRIME and the curve is instantiated using incorrect order, the curve will replace it with the
  calculated order

We hard code the MAX_PRIME value to be the 7th Mersenne prime: 2^19 -1. This value is found in the CurveFactory class.

For p <= MAX_PRIME, we cannot verify the generator point until the curve has been created. Hence, the EllipticCurve
class verifies the generator when the curve is instantiated and handle any exceptions gracefully. It is possible to
create a curve without prime order by instantiating the Elliptic Curve directly, but in this case the generator will
just be a random point and not actually a generator of the group.

```python
from src.basicblockchains_ecc.elliptic_curve import CurveFactory, secp256k1

# Set constants - known to generate curve of prime group order
a = 0
b = 7
p = 43

# Create factory
curve_factory = CurveFactory()

# Create curve
curve = curve_factory.create_curve(a, b, p)

# Prime order
curve.order
31

# Random generator point chosen
curve.generator
(13, 21)

# Add points
curve.add_points((13, 21), (13, 21))
(12, 31)

# Scalar multiplication
curve.scalar_multiplication(2, (13, 21))
(12, 31)

# Generate ECDSA signature
random_number = 13  # Acts as private key
hex_string = '0xaabbcc'
curve.generate_signature(random_number, hex_string)
(25, 1)

# Validate ECDSA signature
public_key = curve.scalar_multiplication(random_number, curve.generator)
curve.verify_signature((25, 1), hex_string, public_key)
True
```

## Cryptographically secure curves

We use the values provided by [NIST](https://www.secg.org/sec2-v2.pdf) to generate cryptographically securve curves.

We provide an example below using secp256k1. We use the function provided to get the secp256k1 curve. We then use
the randbits function from the secrets package to generate a 256-bit private key, and the sha256 function from Python's
hashlib package to generate a random hex string. We see that we can generate a valid ECDSA.

```python
from hashlib import sha256
from src.basicblockchains_ecc.elliptic_curve import secp256k1
from secrets import randbits

# Get secp256k1 directly
crypto_curve = secp256k1()

# Agrees with NIST values
crypto_curve.a
0
crypto_curve.b
7
hex(crypto_curve.p)
'0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f'
hex(crypto_curve.order)
'0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141'
gx, gy = crypto_curve.generator
(hex(gx), hex(gy))
('0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798',
 '0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8')

# Random hex string
hex_string = sha256(b'Random string').hexdigest()
hex_string
'2dc973292d0db59152bb0405e47d85a53ada96bef92ec8eb9c4ddeb762f1907b'

# Random number for private_key
random_number = randbits(256)
hex(random_number)
'0x631d672f03d3e55e77ca5a40c58a5af577d659a355d1f842c9476460cc4ee746'

# Generate signature
signature = crypto_curve.generate_signature(random_number, hex_string)
sx, sy = signature
(hex(sx), hex(sy))
('0x695d0be339314478450fadbb8549bdd8e94bfc952cbc53f3e932fddfea1a3edc',
 '0xaffdca208bc65962a06b445fbbc4bc27a332710288590667cc41f869889f7380')

# Get public key
public_key = crypto_curve.scalar_multiplication(random_number, crypto_curve.generator)
ux, uy = public_key
(hex(ux), hex(uy))
('0x97db4fa5bd0cfa0b15f4783e7ff90f5a3b25729e3a8857581c06d541c63aeff0',
 '0xc15ea3c9584b90f69d818aeed277c74cf869b55550b6b7e7bf9709d550f9d9e')

# Validate signature
crypto_curve.verify_signature(signature, hex_string, public_key)
True
```

## Math

Let E(a,b,p) denote the set of [rational points](https://mathworld.wolfram.com/RationalPoint.html) of the curve y^2 =
x^3 + ax + b over the [finite field](https://en.wikipedia.org/wiki/Finite_field) F_p, for p an odd prime. We assume
that p > 3 for convenience. From the curve equation, we see that for any x in F_p, a corresponding
y will exist if and only if x is
a [quadratic residue modulo p](https://en.wikipedia.org/wiki/Quadratic_residue#Prime_modulus). For this reason, the
cryptomath file will include various quadratic
residue functions.

- We use [Euler's criterion](https://en.wikipedia.org/wiki/Euler%27s_criterion) to determine if n is a
  quadratic residue or non-residue modulo a prime p.
- We use the [Legendre symbol](https://en.wikipedia.org/wiki/Legendre_symbol) to display whether n
  is a quadratic residue/non-residue mod p.
- If n is a quadratic residue mod p, we use the [Tonelli-Shanks](https://en.wikipedia.org/wiki/Tonelli–Shanks_algorithm)
  algorithm to find a value x such that x^2 = n (mod p).

We let **0** denote the '[point at infinity](https://crypto.stanford.edu/pbc/notes/elliptic/group.html)' which is
represented by the value ```None``` in the EllipticCurve class. The set E(a,b,p) along with **0** is an abelian
group G. G will either be cyclic or be the product of two cyclic groups. When the group order is prime, G will be
cyclic and every element except for **0** will be a generator.

More information about elliptic curves:

- [Wikipedia](https://en.wikipedia.org/wiki/Elliptic_curve)
- [Wolfram](https://mathworld.wolfram.com/EllipticCurve.html)

## Tests

We have 3 tests in the test_ecc.py file in the ./tests folder:

- test_curve_functions: creates random curve with small prime using factory and verifies properties
- test_factory: we verify that the CurveFactory class fails for all desired fail conditions
- test_secp_curves: for each secp curve, we verify some necessary curve values as well as the order through scalar
  multiplication of a random point

## Packages

We use the Python secrets package in the ECDSA to generate a random integer. This is stated by Python to be a
cryptographically secure random number generator. See [here](https://docs.python.org/3/library/secrets.html)

We use the isprime function from the [primefac](https://pypi.org/project/primefac/) package to verify that various
integers are prime. This is a suitable package for primes of high bit count.

Finally, in the test_ecc folder we use the random function, but this is not used in the EllipticCurve class.

## Contributing

If there are any suggested improvements, please submit a request. If any errors are found, please open an issue
immediately.

## License

MIT License

Copyright (c) 2022 Basic Blockchains

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

