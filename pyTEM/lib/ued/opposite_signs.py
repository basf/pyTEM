"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

from typing import Union


def opposite_signs(x: Union[int, float], y: Union[int, float]) -> bool:
    """
    Check if two numbers have the same sign
    :param x: int or float:
        The number to compare against y.
    :param y: int of float:
        The number to compare against x.
    :return: bool:
        True: x and y have opposite signs.
        False: x and y have the same sign.
    """
    return (y >= 0) if (x < 0) else (y < 0)


if __name__ == "__main__":
    print(opposite_signs(x=9, y=0.1))
    print(opposite_signs(x=-1, y=-78))
    print(opposite_signs(x=4, y=-8))
    print(opposite_signs(x=-4, y=8))
