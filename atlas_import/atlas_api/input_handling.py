import string
import re

# Regexes for query analysis
# The regex are bulit on the assumption autocomplete starts at 3 characters
# Postcode regex matches 4 digits, possible dash or space then 0-2 letters
PCODE_REGEX = re.compile('^[1-9]\d{2}\d?[ \-]?[a-zA-Z]?[a-zA-Z]?$')

# Address postcode regex
PCODE_NUM_REGEX = re.compile(
    '^1\d{4}[ \-]?[a-zA-Z]{2}[ \-](\d|[a-zA-Z])*$')

# Recognise house number in the search string
HOUSE_NUMBER = re.compile('((\d+)((( |\-)?[a-zA-Z\-]{0,3})|(( |\-)\d*)))$')


def is_int(token):
    try:
        int(token)
        return True
    except ValueError:
        return False


def first_number(input_tokens):

    for i, token in enumerate(input_tokens):
        if is_int(token):
            return i, token

    return -1, ""


REPLACE_TABLE = "".maketrans(
    string.punctuation, len(string.punctuation)*" ")


def clean_tokenize(query_string):
    """
    Cleans up query string and makes tokens.


    - Replace puntuation with " " space.
    - Add space between numers and letters.

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
    # split on digits and spaces
    tokens = re.findall('[^0-9 ]+|\\d+', qs)
    return tokens


def is_postcode(tokens):
    """
    Test of tokens could represent postcode

    asumes tokens are spit in string and digits
    """

    if len(tokens) == 1:
        if len(tokens[0]) == 4:
            try:
                int(tokens[0])
                return True
            except:
                pass

    elif len(tokens) == 2:
        # first part number
        if not len(tokens[0]) == 4:
            return False

        try:
            int(tokens[0])
        except:
            return False

        if len(tokens[1]) > 2:
            return False

        try:
            int(tokens[1])
            return False
        except:
            return True

    return False


def is_straat_huisnummer(tokens):

    if len(tokens) < 2:
        return False

    i, num = first_number(tokens)

    if i < 1:
        return False

    # wat is de kortste straat?
    if len(tokens[0]) > 2:
        return i


def is_postcode_huisnummer(tokens):
    """
    only True  for:

    1013 AW 105 + extra
    """
    if len(tokens) < 3:
        return False

    # first two tokens are valid postalcodes?
    if is_postcode(tokens[:2]):
        # 3rd token is number?
        try:
            int(tokens[3])
        except:
            pass
        # only 'AA'
        if len(tokens[1]) == 2:
            return True

    return False


def is_bouwblok(tokens):
    """
    Bouwblok regex matches 2 digits a letter and
    an optional second letter

    BOUWBLOK_REGEX = re.compile('^[a-zA-Z][a-zA-Z]\d{1,2}$')
    """
    if len(tokens) != 2:
        return False

    letters = tokens[0]
    cijfers = tokens[1]

    if len(letters) != 2:
        return False

    if len(cijfers) != 2:
        return False

    try:
        int(letters)
        return False
    except:
        pass

    try:
        int(cijfers)
        return True
    except:
        pass


def is_meetbout(tokens):
    """
    Meetbout regex matches up to 8 digits
    MEETBOUT_REGEX = re.compile('^\d{3,8}\b$')
    """

    if len(tokens) > 1:
        return False

    meetbout = tokens[0]

    if len(meetbout) > 8 or len(meetbout) < 5:
        return False

    try:
        int(meetbout)
        return True
    except:
        return False
