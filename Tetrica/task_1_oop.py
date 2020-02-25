import re
import string


class NamesProcessor:
    def __init__(self, file_path: str):
        self.file_path = file_path
        ABC = string.ascii_uppercase  # Alphabet
        self.char_number = {ch: n for n, ch in enumerate(ABC, start=1)}  # Initialization of character numbers

    def get_sorted_names(self) -> list:
        """
        Reading and sorting names from a file
        """
        with open(self.file_path, 'r') as f:
            names = re.findall(r'\w+', f.read())

        names.sort()

        return names

    def get_abc_sum_count(self, names: list):
        for idx, name in enumerate(names, start=1):
            count = 0
            for char in name:
                count += self.char_number[char]

            yield count * idx

    def run(self):
        names = self.get_sorted_names()
        names_sum = sum(self.get_abc_sum_count(names=names))

        return names_sum


if __name__ == '__main__':
    processor = NamesProcessor(file_path='./names.txt')
    result = processor.run()

    print('Names sum: ', result)
