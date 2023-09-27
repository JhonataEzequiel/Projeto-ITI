import pickle
import sys
from copy import deepcopy


def get_key_from_value(my_dict, value_to_find):
    for key, value in my_dict.items():
        if value == value_to_find:
            return key
    return None


def set_ascii(dictionary, constant):
    aux_ascii = []
    for i in range(len(constant)):
        aux_ascii.append(dictionary[constant[i]])
    aux_ascii.append(len(aux_ascii))
    aux_int = [aux_ascii[-1]]
    aux_ascii = aux_ascii[:-1]
    aux_ascii = aux_int + aux_ascii
    return aux_ascii


def set_ascii_constants(dictionary, dictionary_size, max_dict_size, mode, lru_quantity, min_rc):
    ascii_dictionary_size = set_ascii(dictionary, str(dictionary_size))
    ascii_max_dict_size = set_ascii(dictionary, str(max_dict_size))
    ascii_mode = set_ascii(dictionary, str(mode))
    ascii_lru_quantity = set_ascii(dictionary, str(lru_quantity))
    ascii_min_rc = set_ascii(dictionary, str(min_rc))
    return ascii_dictionary_size + ascii_max_dict_size + ascii_mode + ascii_lru_quantity + ascii_min_rc


def set_max_dict(dictionary: dict, mode: int, lru_lfu_quantity: int, uses_of_str: dict, original_dict: dict,
                 decompress: bool = False):
    if mode in {1, 4}:
        dictionary = deepcopy(original_dict)
        if mode == 4:
            return dictionary, {}
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
                break
        for use in uses_to_remove:
            if use in uses_of_str:
                uses_of_str.pop(use)
        return dictionary, uses_of_str
    elif mode == 3:
        uses_of_str = dict(sorted(uses_of_str.items(), key=lambda _: _[1]))
        uses_to_remove = []
        i = 1
        for use in uses_of_str:
            if decompress:
                key = get_key_from_value(dictionary, use)
                dictionary.pop(key)
            else:
                dictionary.pop(use)
            uses_to_remove.append(use)
            i += 1
            if i > lru_lfu_quantity:
                break
        for use in uses_to_remove:
            uses_of_str.pop(use)
        return dictionary, uses_of_str

    return dictionary


def set_initial_dict(dictionary_size: int):
    dictionary = dict(
        {chr(i): i for i in range(256)},
        **{chr(i - 256) + chr(i - 255): i for i in range(256, dictionary_size)}
    )
    return dictionary, deepcopy(dictionary)


def add_item_to_dict(dictionary, dictionary_size, temp2):
    dictionary[temp2] = dictionary_size
    dictionary_size += 1
    return dictionary, dictionary_size


def calculate_rc(result, _input):
    size_of_result = sys.getsizeof(result)
    size_of_input = sys.getsizeof(_input)
    return size_of_input / size_of_result


def compress(_input, dictionary_index: int = 256, max_dict_size: int = 512, mode: int = 0,
             lru_quantity: int = 10, min_rc: float = 1000):
    """
    Compress data and returns an archive with lzw compressor
    :param min_rc: minimal ratio of compression allowed (result/_input)
    :param lru_quantity: quantity of phrases to be removed from the dict
    :param max_dict_size: maximum dictionary size allowed
    :param _input: input to compress, usually a txt
    :param dictionary_index: initial dictionary_size
    :param mode: 0 - static dict, 1 - reboot dict to first size, 2 - LRU, 3 - LFU, 4 - Low RC reboot, 5 - infinity
    :return: result
    """
    temp = ""
    uses_of_str = {}

    dictionary, original_dict = set_initial_dict(dictionary_index)
    result = set_ascii_constants(dictionary, dictionary_index, max_dict_size, mode, lru_quantity, min_rc)

    for c in _input:
        temp2 = temp + chr(c)
        if temp2 in dictionary.keys():
            temp = temp2
        else:
            if temp not in original_dict.keys():
                if mode not in {2, 3} and temp in uses_of_str.keys():
                    uses_of_str[temp] += 1
                else:
                    uses_of_str[temp] = 1
            result.append(dictionary[temp])
            dictionary_size = len(dictionary)
            if mode != 0 or dictionary_size < max_dict_size:
                dictionary, dictionary_index = add_item_to_dict(dictionary, dictionary_index, temp2)
                dictionary_size = len(dictionary)
            rc = min_rc + 1
            if mode == 4 and dictionary_size > max_dict_size:
                rc = calculate_rc(result, _input)

            if (mode not in {5, 4} and dictionary_size > max_dict_size) or (rc < min_rc and mode == 4):
                if mode in {2, 3, 4}:
                    dictionary, uses_of_str = set_max_dict(dictionary, mode, lru_quantity, uses_of_str, original_dict)
                else:
                    dictionary = set_max_dict(dictionary, mode, lru_quantity, uses_of_str, original_dict)
            temp = f"{chr(c)}"

    if temp != "":
        result.append(dictionary[temp])

    return result


_input = open("dickens", "rb").read()
_output = open("compressed_dickens.bin", "wb")

compressedFile = compress(_input, mode=5)
pickle.dump(compressedFile, _output)
