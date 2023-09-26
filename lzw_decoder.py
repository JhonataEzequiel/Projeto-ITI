from lzw import *


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


def decompress(_input_):
    dictionary, dictionary_size, max_dict_size, mode, lru_quantity, min_rc, _input_ = get_ascii_constants(_input_)
    original_dict_size = dictionary_size
    original_dict = deepcopy(dictionary)
    uses_of_str = {}
    previous = chr(_input_[0])
    _input_ = _input_[1:]
    result = [previous]

    for bit in _input_:
        aux = dictionary[bit] if bit in dictionary.keys() else previous + previous[0]
        result.append(aux)
        if mode not in {2, 3} and aux in uses_of_str.keys():
            uses_of_str[aux] += 1
        else:
            uses_of_str[aux] = 1
        if mode != 0 or dictionary_size < max_dict_size:
            dictionary[dictionary_size] = previous + aux[0]
            dictionary_size += 1
        if mode == 4 and dictionary_size > max_dict_size:
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
        previous = aux
    return result


_input = pickle.load(open("compressed_dickens.bin", "rb"))
with open("dickens.txt", "w") as _output:
    uncompressedFile = decompress(deepcopy(_input))
    for line in uncompressedFile:
        _output.write(line)
