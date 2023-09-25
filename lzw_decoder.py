import pickle


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
    previous = chr(_input_[0])
    _input_ = _input_[1:]
    result = [previous]
    for bit in _input_:
        aux = dictionary.get(bit, previous + previous[0])
        result.append(aux)
        dictionary[dictionary_size] = previous + aux[0]
        dictionary_size += 1
        previous = aux
    return result


_input = pickle.load(open("compressed_dickens.bin", "rb"))
with open("dickens.txt", "w") as _output:
    uncompressedFile = decompress(_input)
    for line in uncompressedFile:
        _output.write(line)
