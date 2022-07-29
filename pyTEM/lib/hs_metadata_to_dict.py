"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

from hyperspy.misc.utils import DictionaryTreeBrowser


def hs_metadata_to_dict(hs_dict: DictionaryTreeBrowser) -> dict:
    """
    Convert Hyperspy metadata, which is a bunch of nested DictionaryTreeBrowser objects, to a normal Python dictionary.
    Conversion is performed recursively.

    :param hs_dict: DictionaryTreeBrowser:
        A Hyperspy DictionaryTreeBrowser object.

    :return: dict:
        The provided metadata as a normal python dictionary.
    """
    normal_dict = dict(hs_dict)
    for key, value in normal_dict.items():
        if isinstance(value, DictionaryTreeBrowser):
            # Then recursively run through converting all DictionaryTreeBrowser within..
            normal_dict[key] = hs_metadata_to_dict(hs_dict=value)
        else:
            normal_dict[key] = value

    return normal_dict
