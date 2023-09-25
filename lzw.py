import pickle
from typing import List


def set_max_dict(dictionary: dict, mode: int, max_dict_size: int, dictionary_size: int, lru_quantity: int,
                 uses_of_str: dict):
    if mode == 0:
        return dictionary, dictionary_size - 1
    if mode == 1:
        dictionary = dictionary[:max_dict_size - 1]
        a = 1
    if mode == 2:
        uses_of_str = dict(sorted(uses_of_str.items()))
        a = 1
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
    dictionary = {}
    result = []
    temp = ""
    uses_of_str = {}

    for i in range(0, dictionary_size):
        dictionary[str(chr(i))] = i

    for c in _input:
        temp2 = temp + str(chr(c))
        if temp2 in dictionary.keys():
            temp = temp2
        else:
            if temp2 not in uses_of_str.keys():
                uses_of_str[temp2] = 1
            else:
                uses_of_str[temp2] += 1
            result.append(dictionary[temp])
            dictionary[temp2] = dictionary_size
            dictionary_size += 1
            if mode != 5:
                if dictionary_size > max_dict_size-1:
                    dictionary, dictionary_size = set_max_dict(dictionary, mode, max_dict_size, dictionary_size,
                                                               lru_quantity, uses_of_str)
            temp = "" + str(chr(c))

    if temp != "":
        result.append(dictionary[temp])

    return result


_input = open("dickens", "rb").read()
_output = open("compressed_dickens", "wb")

compressedFile = compress(_input, mode=1)
pickle.dump(compressedFile, _output)
