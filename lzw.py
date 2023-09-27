import pickle
from modules import *


def compress(_input, dictionary_index: int = 256, max_dict_size: int = 512, mode: int = 0,
             lru_quantity: int = 50, min_rc: float = 1000):
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
            if mode != 5:
                uses_of_str = set_uses_of_str(temp, original_dict, mode, uses_of_str)
                dictionary, dictionary_index, dictionary_size = update_result_and_dictionary(
                    dictionary, mode, max_dict_size, dictionary_index, temp2, result, temp
                )
                rc = calculate_rc(result, _input, mode, dictionary_size, max_dict_size, min_rc)
                dictionary, uses_of_str = treat_max_dict(
                    mode, dictionary_size, max_dict_size, rc, min_rc, dictionary, lru_quantity,
                    uses_of_str, original_dict
                )
            else:
                result.append(dictionary[temp])
                dictionary, dictionary_index = add_item_to_dict(dictionary, dictionary_index, temp2)
            temp = f"{chr(c)}"
    if temp != "":
        result.append(dictionary[temp])

    return result


_input = open("dickens", "rb").read()
_output = open("compressed_dickens.bin", "wb")

compressedFile = compress(_input, mode=2)
pickle.dump(compressedFile, _output)
