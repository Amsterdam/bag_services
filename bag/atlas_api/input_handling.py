import string
import re

REPLACE_TABLE = "".maketrans(
    string.punctuation, len(string.punctuation)*" ")


def first_number(input_tokens):

    for i, token in enumerate(input_tokens):
        if token.isdigit():
            return i, token

    return -1, ""


def number_list(input_tokens):
    """Find list [(index number)..] in tokens"""

    numbers = []

    for i, token in enumerate(input_tokens):
        if token.isdigit():
            numbers.append((i, token))

    return numbers


def clean_tokenize(query_string):
    """
    Cleans up query string and makes tokens.

    - Replace puntuation with " " space.
    - Add space between numers and letters.
    - lowercase input

    Examples:

    6A
    ['6', 'A']

    'aaa bbb ccc'
    ['aaa', 'bbb', 'ccc']

    'add23b cd3df h-4'
    ['add', '23', 'b', 'cd', '3', 'df', 'h' '4']

    Nieuwe achtergracht 105-3 HA2
    ['Nieuwe', 'achtergracht', '105', '3', 'HA', '2']
    """
    # clear all wrong useless data

    tokens = []
    qs = query_string.translate(REPLACE_TABLE)
    qs = qs.lower()
    # split on digits and spaces
    tokens = re.findall('[^0-9 ]+|\\d+', qs)
    return qs, tokens


def is_postcode(query_string, tokens):
    """
    Test of tokens could represent postcode

    asumes tokens are spit in string and digits
    """

    if len(tokens) == 1:
        if len(tokens[0]) == 4:
            try:
                int(tokens[0])
                return True
            except ValueError:
                pass

    elif len(tokens) == 2:
        # first part number
        if not len(tokens[0]) == 4:
            return False

        try:
            int(tokens[0])
        except ValueError:
            return False

        if len(tokens[1]) > 2:
            return False

        try:
            int(tokens[1])
            return False
        except ValueError:
            return True

    return False


def is_straat_huisnummer(query_string, tokens):

    if len(tokens) < 2:
        return False

    i, num = first_number(tokens)

    if i < 1:
        return False

    # wat is de kortste straat?
    if len("".join(tokens[:i])) > 2:
        return i


def is_postcode_huisnummer(query_string, tokens):
    """
    only True  for:

    1013 AW 105 + extra
    """
    if len(tokens) < 3:
        return False

    # first two tokens are valid postalcodes?
    if is_postcode("", tokens[:2]):
        # 3rd token is number?
        try:
            int(tokens[2])
        except:
            return False
        # only 'AA'
        if len(tokens[1]) == 2:
            return True

    return False


def could_be_bouwblok(query_string, tokens):

    if len(tokens) > 2:
        return False

    if len(tokens) == 1:
        letters = tokens[0]
        if len(letters) > 2:
            return False
        if letters.isdigit():
            return False

    if len(tokens) == 2:
        letters = tokens[0]
        if len(letters) != 2:
            return False
        if letters.isdigit():
            return False

        cijfers = tokens[1]
        if not cijfers.isdigit():
            return False

    return True


