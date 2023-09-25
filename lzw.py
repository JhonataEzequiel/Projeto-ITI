import pickle
from typing import List


def set_max_dict(dictionary: dict, mode: int, max_dict_size: int, dictionary_size: int, lru_quantity: int,
                 uses_of_str: dict, original_dict_size: int = 256):
    if mode == 0:
        return dictionary, dictionary_size - 1
    elif mode == 1:
        i = max_dict_size
        inverted_keys = list(dictionary.keys())[::-1]
        inverted_dict = {key: dictionary[key] for key in inverted_keys}
        items_to_remove = []
        for dict_item in inverted_dict:
            items_to_remove.append(dict_item)
            i -= 1
            if i == original_dict_size:
                break
        for item in items_to_remove:
            dictionary.pop(item)
        dictionary_size = i
    elif mode == 2:
        uses_of_str = dict(sorted(uses_of_str.items(), reverse=True))
        uses_to_remove = []
        i = 1
        for use in uses_of_str:
            dictionary.pop(use)
            uses_to_remove.append(use)
            i += 1
            if i > lru_quantity:
                dictionary_size = dictionary_size - lru_quantity
                break
        for use in uses_to_remove:
            uses_of_str.pop(use)
        return dictionary, dictionary_size, uses_of_str
    return dictionary, dictionary_size


def compress(_input, dictionary_size: int = 256, max_dict_size: int = 512, mode: int = 0,
             lru_quantity: int = 10) -> List:
    """
    Compress data and returns an archive with lzw compressor
    :param lru_quantity: quantity of phrases to be removed from the dict
    :param max_dict_size: maximum dictionary size allowed
    :param _input: input to compress, usually a txt
    :param dictionary_size: initial dictionary_size
    :param mode: 0 - static dict, 1 - reboot dict to first size, 2 - LRU, 3 - LFU, 4 - Low RC reboot, 5 - infinity
    :return: result
    """
    result = []
    temp = ""
    uses_of_str = {}
    original_dict_size = dictionary_size

    dictionary = {chr(i): i for i in range(dictionary_size)}
    for c in _input:
        temp2 = temp + chr(c)
        if temp2 in dictionary.keys():
            temp = temp2
        else:
            if temp2 in uses_of_str:
                uses_of_str[temp2] += 1
            else:
                uses_of_str[temp2] = 1
            result.append(dictionary[temp])
            dictionary[temp2] = dictionary_size
            dictionary_size += 1
            if mode != 5 and dictionary_size > max_dict_size-1:
                if mode == 2:
                    dictionary, dictionary_size, uses_of_str = set_max_dict(dictionary, mode, max_dict_size,
                                                                            dictionary_size, lru_quantity, uses_of_str,
                                                                            original_dict_size)
                else:
                    dictionary, dictionary_size = set_max_dict(dictionary, mode, max_dict_size, dictionary_size,
                                                               lru_quantity, uses_of_str, original_dict_size)
            temp = f"{chr(c)}"

    if temp != "":
        result.append(dictionary[temp])

    return result


_input = open("dickens", "rb").read()
_output = open("compressed_dickens", "wb")

compressedFile = compress(_input, mode=5)
pickle.dump(compressedFile, _output)
