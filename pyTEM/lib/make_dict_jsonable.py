"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""
import json


def make_dict_jsonable(my_dict: dict) -> dict:
    """
    Some types are not be JSON serializable. Given a dictionary, recursively run through and convert all non-JSON-
     serializable types to strings.

    :param my_dict: dict:
        A dictionary (possibly contining nested dictionaries), which may or may not contain non-JSON-serializable types.
    :return: dict:
        The provided dictionary, but will all non-JSON-serializable items converted to string.
    """
    jsonable_dict = dict()
    for key, value in my_dict.items():
        if isinstance(value, dict):
            # Then recursively run through looking for non jsonable values within..
            jsonable_dict[key] = make_dict_jsonable(value)
        else:
            if is_jsonable(value):
                jsonable_dict[key] = value
            else:
                jsonable_dict[key] = str(value)

    return jsonable_dict


def is_jsonable(x):
    """
    Return True if x is JSON serializable, False otherwise.
    """
    try:
        json.dumps(x)
        return True
    except (TypeError, OverflowError):
        return False
