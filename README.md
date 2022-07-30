<center>
<h1>Elliptic Curve Cryptography</h1>
</center>

<hr>

Elliptic Curve:

    -We instantiate an elliptic curve E of the form y^2 = x^3 + ax + b over the finite field F_p using the values a,
    b and p.

    -We allow for the option to include the group order and/or a generator point.

    -For small primes p, we can manually calculate the group order. This is unfeasible for large primes,
    hence the ability to include the order.

    -We require that if the group order is submitted, that it be prime, as this condition is necessary for the ECDSA.

    -For a prime group order, every rational point is a generator. Hence we can include a generator point,
    or choose a random point to act as generator.

CurveFactory:

    -We use the factory method to generate our EllipticCurve object, as incorrect variables will cause issues.

    -We verify that p is prime and that a,b and p don't yield a singular curve.

    -If the group order is submitted, we verify that the order is prime.

    -If all values are valid, we return an instantiated EllipticCurve object

    NOTE: We cannot verify that the generator is a point on the curve until the object is instantiated. For this
    reason, we verify the generator when the curve is instantiated and handle any exceptions gracefully.

Functions:

    -We include the ability to retrieve the secp256k1 curve, as used in Bitcoin and Ethereum

