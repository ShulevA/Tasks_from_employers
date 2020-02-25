import re
import string


def sum_of_names(file_path: str, ABC=string.ascii_uppercase, char_number=None, result=0):
    if char_number is None:
        char_number = {ch: n for n, ch in enumerate(ABC, start=1)}
    '''
    Reading and sorting names from a file
    '''
    with open(file_path) as inf:
        names = re.findall(r'\w+', inf.read())

    names.sort()
    '''
    ABC sum count and product of the ABC sum and serial number
    '''
    for idx, name in enumerate(names, start=1):
        count = 0
        for char in name:
            count += char_number[char]

        result += count * idx

    return result


if __name__ == '__main__':
    print(sum_of_names(file_path='./names.txt'))
