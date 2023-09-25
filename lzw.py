import pickle
import sys
from copy import deepcopy


def set_max_dict(dictionary: dict, mode: int, dictionary_size: int, lru_lfu_quantity: int,
                 uses_of_str: dict, original_dict: dict, original_dict_size: int = 256):
    if mode in {1, 4}:
        dictionary = deepcopy(original_dict)
        dictionary_size = original_dict_size
        if mode == 4:
            return dictionary, dictionary_size, {}
    elif mode == 2:
        uses_to_remove = []
        reversed_dict = list(dictionary.keys())[::-1]
        reversed_dict = {key: dictionary[key] for key in reversed_dict}
        i = 1
        for use in reversed_dict:
            dictionary.pop(use)
            uses_to_remove.append(use)
            i += 1
            if i > lru_lfu_quantity:
                dictionary_size = dictionary_size - lru_lfu_quantity
                break
        for use in uses_to_remove:
            if use in uses_of_str:
                uses_of_str.pop(use)
        return dictionary, dictionary_size, uses_of_str
    elif mode == 3:
        uses_of_str = dict(sorted(uses_of_str.items(), key=lambda _: _[1]))
        uses_to_remove = []
        i = 1
        for use in uses_of_str:
            dictionary.pop(use)
            uses_to_remove.append(use)
            i += 1
            if i > lru_lfu_quantity:
                dictionary_size = dictionary_size - lru_lfu_quantity
                break
        for use in uses_to_remove:
            uses_of_str.pop(use)
        return dictionary, dictionary_size, uses_of_str

    return dictionary, dictionary_size


def compress(_input, dictionary_size: int = 256, max_dict_size: int = 512, mode: int = 0,
             lru_quantity: int = 10, min_rc: float = 1000):
    """
    Compress data and returns an archive with lzw compressor
    :param min_rc: minimal ratio of compression allowed (result/_input)
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
    original_dict = deepcopy(dictionary)
    for c in _input:
        temp2 = temp + chr(c)
        if temp2 in dictionary.keys():
            temp = temp2
        else:
            if temp not in original_dict.keys():
                if temp in uses_of_str.keys():
                    uses_of_str[temp] += 1
                else:
                    uses_of_str[temp] = 1
            result.append(dictionary[temp])
            rc = min_rc + 1
            if mode != 0 or dictionary_size < max_dict_size:
                dictionary[temp2] = dictionary_size
                dictionary_size += 1
            if dictionary_size > max_dict_size:
                size_of_result = sys.getsizeof(result)
                size_of_input = sys.getsizeof(_input)
                rc = size_of_input / size_of_result
            if (mode not in {5, 4} and dictionary_size > max_dict_size) or (rc < min_rc and mode == 4):
                if mode in {2, 3, 4}:
                    dictionary, dictionary_size, uses_of_str = set_max_dict(dictionary, mode, dictionary_size,
                                                                            lru_quantity, uses_of_str, original_dict,
                                                                            original_dict_size)
                else:
                    dictionary, dictionary_size = set_max_dict(dictionary, mode, dictionary_size, lru_quantity,
                                                               uses_of_str, original_dict, original_dict_size)
            temp = f"{chr(c)}"

    if temp != "":
        result.append(dictionary[temp])

    return result


_input = open("dickens", "rb").read()
_output = open("compressed_dickens", "wb")

compressedFile = compress(_input, mode=5)
pickle.dump(compressedFile, _output)
