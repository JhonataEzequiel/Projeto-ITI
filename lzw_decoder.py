from lzw import *


def decompress(_input_):
    dictionary, dictionary_size, max_dict_size, mode, lru_quantity, min_rc, _input_ = get_ascii_constants(_input_)
    dictionary_index = dictionary_size
    original_dict = deepcopy(dictionary)
    uses_of_str = {}
    previous = chr(_input_[0])
    _input_ = _input_[1:]
    result = [previous]

    for bit in _input_:
        aux = dictionary[bit] if bit in dictionary.keys() else previous + previous[0]
        result.append(aux)
        if mode == 5:
            dictionary[dictionary_index] = previous + aux[0]
            dictionary_index += 1
        else:
            uses_of_str = set_uses_of_str(
                original_dict=original_dict, mode=mode, uses_of_str=uses_of_str, decompress=True, aux=aux
            )
            dictionary, dictionary_index, dictionary_size = update_result_and_dictionary(
                dictionary=dictionary, mode=mode, max_dict_size=max_dict_size, dictionary_index=dictionary_index,
                previous=previous, aux=aux, decompress=True
            )
            rc = calculate_rc(
                result=_input_, _input=result, mode=mode, dictionary_size=dictionary_size, max_dict_size=max_dict_size,
                min_rc=min_rc
            )
            dictionary, uses_of_str = treat_max_dict(
                mode, dictionary_size, max_dict_size, rc, min_rc, dictionary, lru_quantity, uses_of_str,
                original_dict, decompress=True
            )
        previous = aux
    return result


_input = pickle.load(open("compressed_dickens.bin", "rb"))
with open("dickens.txt", "w") as _output:
    uncompressedFile = decompress(deepcopy(_input))
    for line in uncompressedFile:
        _output.write(line)
