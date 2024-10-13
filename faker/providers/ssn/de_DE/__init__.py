import datetime
import re
import string
import typing
import unicodedata

from .. import Provider as BaseProvider


class Provider(BaseProvider):
    """
    A Faker provider for the German VAT IDs
    """

    vat_id_formats = ("DE#########",)

    def vat_id(self) -> str:
        """
        http://ec.europa.eu/taxation_customs/vies/faq.html#item_11
        :return: A random German VAT ID
        """

        return self.bothify(self.random_element(self.vat_id_formats))

    @staticmethod
    def _normalize_name(name: str) -> str:
        """
        Normalize the name into the base latin script system.
        :return: A name in it's normalized form
        """
        nfkd_form = unicodedata.normalize("NFKD", name)
        return "".join([char for char in nfkd_form if not unicodedata.combining(char)])

    @staticmethod
    def _etin_name_quartet(name: str) -> str:
        """
        Construct a quartet according to the algorithm
        https://de.wikipedia.org/wiki/ETIN#Zusammensetzung
        :return: A 4-character string derived by name
        """
        # Normalize diacritic characters into basic latin letters
        _name = Provider._normalize_name(name)
        # Replace 'Sch' with 'Y'
        _name = _name.replace("Sch", "Y")
        # Strip the last name prefixes 'de', 'von', 'zu'
        for prefix in ("de ", "von ", "zu "):
            _name.replace(prefix, "")
        _name = _name.upper()
        # remove all characters, except A to Z. For example: HANS-DIETER -> HANSDIETER
        _name = re.sub(r"[^A-Z]", "", _name)
        consonants = re.sub(r"[AEIOU]", "", _name)
        vowels = re.sub(r"[^AEIOU]", "", _name)
        result = consonants[:4]
        if len(result) < 4:
            for vowel in reversed(vowels):
                result += vowel
                if len(result) == 4:
                    break
        result = result.ljust(4, "X")
        return result

    @staticmethod
    def _etin_check_weight(position, value) -> int:
        index = 0 if position % 2 == 0 else 1
        return (
            {
                "A": 0,
                "B": 1,
                "C": 2,
                "D": 3,
                "E": 4,
                "F": 5,
                "G": 6,
                "H": 7,
                "I": 8,
                "J": 9,
                "K": 10,
                "L": 11,
                "M": 12,
                "N": 13,
                "O": 14,
                "P": 15,
                "Q": 16,
                "R": 17,
                "S": 18,
                "T": 19,
                "U": 20,
                "V": 21,
                "W": 22,
                "X": 23,
                "Y": 24,
                "Z": 25,
                "0": 0,
                "1": 1,
                "2": 2,
                "3": 3,
                "4": 4,
                "5": 5,
                "6": 6,
                "7": 7,
                "8": 8,
                "9": 9,
            },
            {
                "A": 1,
                "B": 0,
                "C": 5,
                "D": 7,
                "E": 9,
                "F": 13,
                "G": 15,
                "H": 17,
                "I": 19,
                "J": 21,
                "K": 2,
                "L": 4,
                "M": 18,
                "N": 20,
                "O": 11,
                "P": 3,
                "Q": 6,
                "R": 8,
                "S": 12,
                "T": 14,
                "U": 16,
                "V": 10,
                "W": 22,
                "X": 23,
                "Y": 24,
                "Z": 25,
                "0": 1,
                "1": 0,
                "2": 5,
                "3": 7,
                "4": 9,
                "5": 13,
                "6": 15,
                "7": 17,
                "8": 19,
                "9": 21,
            },
        )[index][value]

    @staticmethod
    def _etin_check_character(etin_stub: str) -> str:
        """
        Calculate the etin check character for an etin. The check character is the 13-th (last) character of an etin.
        """
        _sum = 0
        for index, character in enumerate(etin_stub):
            _sum += Provider._etin_check_weight(index, character)
        mod_26 = _sum % 26
        return string.ascii_uppercase[mod_26]

    MONTH_LETTER = {
        1: "A",
        2: "B",
        3: "C",
        4: "D",
        5: "E",
        6: "F",
        7: "G",
        8: "H",
        9: "I",
        10: "J",
        11: "K",
        12: "L",
    }

    def etin(
        self,
        first_name: typing.Optional[str] = None,
        last_name: typing.Optional[str] = None,
        birthday: typing.Optional[datetime.date] = None,
    ) -> str:
        """
        Generate a eTIN (Electronic Taxpayer Identification Number)
        https://de.wikipedia.org/wiki/ETIN
        http://www.pruefziffernberechnung.de/E/eTIN.shtml
        :return: A random 14-character eTIN
        """
        if first_name is None:
            first_name = self.generator.first_name()
        if last_name is None:
            last_name = self.generator.last_name()
        if birthday is None:
            birthday = self.generator.date_of_birth()
        _etin = (
            f"{self._etin_name_quartet(last_name)}"
            f"{self._etin_name_quartet(first_name)}"
            f"{str(birthday.year)[-2:]}"
            f"{self.MONTH_LETTER[birthday.month]}"
            f"{str(birthday.day).rjust(2, "0")}"
        ).upper()
        return f"{_etin}{self._etin_check_character(_etin)}"
