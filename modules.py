import sys
from copy import deepcopy


def get_key_from_value(my_dict, value_to_find):
    return next(
        (key for key, value in my_dict.items() if value == value_to_find), None
    )


def set_ascii(dictionary, constant):
    aux_ascii = [dictionary[constant[i]] for i in range(len(constant))]
    aux_ascii.append(len(aux_ascii))
    aux_int = [aux_ascii[-1]]
    aux_ascii = aux_ascii[:-1]
    return aux_int + aux_ascii


def set_ascii_constants(dictionary, dictionary_size, max_dict_size, mode, lru_quantity, min_rc):
    ascii_dictionary_size = set_ascii(dictionary, str(dictionary_size))
    ascii_max_dict_size = set_ascii(dictionary, str(max_dict_size))
    ascii_mode = set_ascii(dictionary, str(mode))
    ascii_lru_quantity = set_ascii(dictionary, str(lru_quantity))
    ascii_min_rc = set_ascii(dictionary, str(min_rc))
    return ascii_dictionary_size + ascii_max_dict_size + ascii_mode + ascii_lru_quantity + ascii_min_rc


def remove_dict_entries(uses_of_str, decompress, dictionary, lru_lfu_quantity, original_dict, mode=0):
    if len(uses_of_str) >= lru_lfu_quantity:
        i = 1
        uses_to_remove = []
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
    else:
        dictionary = deepcopy(original_dict)
        uses_of_str = {}
    return dictionary, uses_of_str


def set_max_dict(dictionary: dict, mode: int, lru_lfu_quantity: int, uses_of_str: dict, original_dict: dict,
                 decompress: bool = False):
    if mode in {1, 4}:
        dictionary = deepcopy(original_dict)
        if mode == 4:
            return dictionary, {}
    elif mode == 2:
        return remove_dict_entries(uses_of_str, decompress, dictionary, lru_lfu_quantity, original_dict, mode=2)
    elif mode == 3:
        uses_of_str = dict(sorted(uses_of_str.items(), key=lambda _: _[1]))
        return remove_dict_entries(uses_of_str, decompress, dictionary, lru_lfu_quantity, original_dict)

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


def calculate_rc(result=None, _input=None, mode=None, dictionary_size=None, max_dict_size=None, min_rc=None):
    if mode != 4 or dictionary_size <= max_dict_size:
        return min_rc + 1
    size_of_result = sys.getsizeof(result)
    size_of_input = sys.getsizeof(_input)
    return size_of_input / size_of_result


def set_uses_of_str(temp=None, original_dict=None, mode=5, uses_of_str=None, decompress=False, aux=None):
    if not decompress and temp not in original_dict.keys():
        if mode not in {2, 3} and temp in uses_of_str.keys():
            uses_of_str[temp] += 1
        else:
            uses_of_str[temp] = 1
    elif decompress and aux not in original_dict.values():
        if mode not in {2, 3} and aux in uses_of_str.keys():
            uses_of_str[aux] += 1
        else:
            uses_of_str[aux] = 1
    return uses_of_str


def update_result_and_dictionary(
        dictionary=None, mode=None, max_dict_size=None, dictionary_index=None, temp2=None, result=None, temp=None,
        decompress=False, previous=None, aux=None
):
    if not decompress:
        result.append(dictionary[temp])
        dictionary_size = len(dictionary)
        if mode != 0 or dictionary_size < max_dict_size:
            if mode == 1 and dictionary_size < dictionary_index:
                dictionary_index = dictionary_size
            dictionary, dictionary_index = add_item_to_dict(dictionary, dictionary_index, temp2)
            dictionary_size = len(dictionary)
    else:
        dictionary_size = len(dictionary)
        if mode != 0 or dictionary_size < max_dict_size:
            if mode == 1 and dictionary_size < dictionary_index:
                dictionary_index = dictionary_size
            dictionary[dictionary_index] = previous + aux[0]
            dictionary_index += 1
            dictionary_size = len(dictionary)
    return dictionary, dictionary_index, dictionary_size


def treat_max_dict(
        mode, dictionary_size, max_dict_size, rc, min_rc, dictionary, lru_quantity, uses_of_str,
        original_dict, decompress=False
):
    if (mode != 4 and dictionary_size > max_dict_size) or (rc < min_rc and mode == 4):
        if mode in {2, 3, 4}:
            dictionary, uses_of_str = set_max_dict(dictionary, mode, lru_quantity, uses_of_str,
                                                   original_dict, decompress)
        else:
            dictionary = set_max_dict(dictionary, mode, lru_quantity, uses_of_str, original_dict)
    return dictionary, uses_of_str


def get_ascii(_input2):
    quantity_of_chars_to_form_constant = _input2[0]
    _input2 = _input2[1:]
    constant = _input2[:quantity_of_chars_to_form_constant]
    string_constant = ''.join(
        f'{chr(constant[i])}' for i in range(len(constant))
    )
    _input2 = _input2[len(constant):]
    return int(string_constant), _input2


def get_ascii_constants(_input1):
    dictionary_size, _input1 = get_ascii(_input1)
    max_dict_size, _input1 = get_ascii(_input1)
    mode, _input1 = get_ascii(_input1)
    lru_quantity, _input1 = get_ascii(_input1)
    min_rc, _input1 = get_ascii(_input1)
    if dictionary_size <= 256:
        dictionary = {i: chr(i) for i in range(dictionary_size)}
    else:
        dictionary = {chr(i): i for i in range(256)}
        for i in range(256, dictionary_size):
            dictionary[chr(i - 256) + chr(i - 255)] = i
    return dictionary, dictionary_size, max_dict_size, mode, lru_quantity, min_rc, _input1
