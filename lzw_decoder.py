import pickle

dictionary_size = 256


def decompress(input):
    global dictionary_size
    dictionary = {}
    result = []

    for i in range(0, DICTIONARY_SIZE):
        dictionary[i] = str(chr(i))

    previous = chr(input[0])
    input = input[1:]
    result.append(previous)

    for bit in input:
        aux = ""
        if bit in dictionary.keys():
            aux = dictionary[bit]
        else:
            aux = previous + previous[0]
            # Bit is not in the dictionary
            # Get the last character printed + the first position of the last character printed
            # because we must decode bits that are not present in the dictionary, so we have to guess what it represents, for example:
            # let's say bit 37768 is not in the dictionary, so we get the last character printed, for example it was 'uh'
            # and we take it 'uh' plus its first position 'u', resulting in 'uhu', which is the representation of bit 37768
            # the only case where this can happen is if the substring starts and ends with the same character ("uhuhu").
        result.append(aux)
        dictionary[DICTIONARY_SIZE] = previous + aux[0]
        DICTIONARY_SIZE += 1
        previous = aux
    return result


input = pickle.load(open("05_comprimido.bin", "rb"))
output = open("05.txt", "w")

uncompressedFile = decompress(input)
for l in uncompressedFile:
    output.write(l)
output.close()
