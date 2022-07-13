"""
 Author:  https://www.geeksforgeeks.org/find-number-closest-n-divisible-m/
 Date:    Retrieved Summer 2021
"""


def closest_number(n: float, m: float) -> float:
    """
    Find the number closest to n that is divisible by m.

    :return: float:
        The number closest to n that is divisible by m.
    """
    q = int(n / m)  # Find the quotient

    # 1st possible closest number
    n1 = m * q

    # 2nd possible closest number
    if (n * m) > 0:
        n2 = (m * (q + 1))
    else:
        n2 = (m * (q - 1))

    # if true, then n1 is the closest number
    if abs(n - n1) < abs(n - n2):
        return n1

    # else n2 is the closest number
    return n2
