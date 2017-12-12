import re
import string

_REPLACE_TABLE = "".maketrans(
    string.punctuation, len(string.punctuation) * " ")


class KadastraalObjectQuery(object):
    """
    The KadastraalObjectQuery wraps an original query into its constituent
    components.
    """

    gemeente_code = None  # Example: ASD15
    gemeente_naam = None  # Example: Amsterdam
    sectie = None  # Example: S
    object_nummer = None  # Example: 0002
    index_letter = None  # Example: A
    index_nummer = None  # Example: 0000

    def __init__(self, tokens: [str]):
        """
        Initialize the query with the individual Kadastraal Object tokens.

        Examples:
        ['asd', 15','s', '00000','a','0000']
        ['amsterdam', 's', '00000', 'a', '0000']

        ['gemeente', 'sectie', 'object-nummer', 'index-letter', 'index-nummer']

        :param tokens:
        """
        if len(tokens) < 2:
            # Hier kunnen we niets mee
            return

        # We zorgen ervoor dat alle indices bestaan. Dit om te voorkomen dat
        # we de hele tijd moeilijk lopen te checken
        tokens = tokens[:] + [None, None, None]

        # Gemeente-code (twee tokens, waarvan het eerste drie letters) of
        # Gemeente-naam (één token)
        if len(tokens[0]) == 3:
            self.gemeente_code = tokens[0] + tokens[1]
            tokens = tokens[2:]
        else:
            self.gemeente_naam = tokens[0]
            tokens = tokens[1:]

        self.sectie = tokens[0]
        self.object_nummer = tokens[1]

        # it is possible to use a shortcut notation for index letter - number
        # 'g' is always followed by 0. if a number larger then 0 is found then
        # posibilities:
        #   g 0
        #   0 -> g 0
        #   a 7
        #   7 -> a 7
        # So the 2nd token can be 'a' or 'g' or 'number'.
        # if perceelnumber is 0 then meaning was 'g 0'. else 'a perceelnumber'
        index_thingie = tokens[2]
        if index_thingie in ['a', 'g']:
            self.index_letter = index_thingie
            self.index_nummer = tokens[3]
        elif index_thingie and index_thingie.isdigit():
            if int(index_thingie) > 0:
                self.index_letter = 'a'
                self.index_nummer = index_thingie
            else:
                self.index_letter = 'g'
                self.index_nummer = 0

        # clean-up index nummer and object nummer
        if self.object_nummer and not self.object_nummer.isdigit():
            self.object_nummer = None

        if self.index_nummer and not self.index_nummer.isdigit():
            self.index_nummer = None

    def object_nummer_is_exact(self):
        """
        Returns true if the object nummer is an exact query (i.e. 5 digits
        long)
        """
        return self.object_nummer and len(self.object_nummer) == 5

    def index_nummer_is_exact(self):
        """
        Returns true if the index nummer is an exact query (i.e. 4 digits long)
        """
        return self.index_nummer and len(self.index_nummer) == 4

    def is_empty(self):
        return (not self.gemeente_code and not self.gemeente_naam
                and not self.sectie and not self.object_nummer
                and not self.index_letter and not self.index_nummer)


class QueryAnalyzer(object):
    """
    The QueryAnalyzer takes a plain query string and performs various analyses
    on it.  It contains various is_XXX methods that are used to determine if
    this query could refer to an XXX.
    """

    def __init__(self, query: str):
        self.query = query
        self._cleaned_query = query.translate(_REPLACE_TABLE).lower()
        self._tokens = re.findall('[^0-9 ]+|\\d+', self._cleaned_query)
        self._token_count = len(self._tokens)

        self._huisnummer_index = None
        for i, token in enumerate(self._tokens[1:]):
            if token.isdigit():
                self._huisnummer_index = i + 1
                break

    def is_kadastraal_object_prefix(self) -> bool:
        """
        Returns True if this query could refer to a kadastraal object.
        """
        if self._token_count < 2:
            return False

        return self._is_kadastraal_object_code() or \
            self._is_kadastraal_object_gemeente()

    def _is_kadastraal_object_code(self):
        """
        Returns True if this is a kadastraal object like 'ASD15...'
        """
        letters = self._tokens[0]
        cijfers = self._tokens[1]

        if len(letters) != 3:
            return False
        if len(cijfers) != 2:
            return False
        if letters.isdigit():
            return False
        if not cijfers.isdigit():
            return False

        # fail when there is a space in the query string
        # ASD15 OK
        # ASD 15 NOT OK
        if not self._cleaned_query.startswith("".join(self._tokens[:2])):
            return False
        return True

    def _is_kadastraal_object_gemeente(self) -> bool:
        """
        Returns true if this is a kadastraal object like 'Amsterdam S...'
        """
        sectie = self._tokens[1]

        if len(sectie) > 2:
            return False

        if sectie.isdigit():
            return False

        if self._token_count >= 3:
            if not self._tokens[2].isdigit():
                return False

        return True

    def get_kadastraal_object_query(self) -> KadastraalObjectQuery:
        """
        Assuming that this query represents a kadastraal object query,
        this returns the KadastraalObjectQuery wrapper.
        """
        return KadastraalObjectQuery(self._tokens)

    def is_bouwblok_prefix(self) -> bool:
        """
        Returns True if this query could refer to a bouwblok
        """
        if self._token_count == 1:
            letters = self._tokens[0]
            return (
                len(letters) <= 2 and not letters.isdigit()
            )
        elif self._token_count == 2:
            letters, cijfers = self._tokens
            return (
                len(letters) == 2
                and not letters.isdigit()
                and len(cijfers) <= 2
                and cijfers.isdigit()
            )

        return False

    def is_bouwblok_exact(self) -> bool:
        """
        Returns True if this query could refer to a bouwblok
        """
        if self._token_count != 2:
            return False

        letters, cijfers = self._tokens

        return (
            len(letters) == 2
            and not letters.isdigit()
            and len(cijfers) == 2
            and cijfers.isdigit()
        )

    def get_bouwblok(self) -> str:
        """
        Assuming that the query represents a bouwblok, this returns the
        bouwblok query
        """
        assert self.is_bouwblok_prefix()
        return self._cleaned_query

    def is_postcode_prefix(self) -> bool:
        """
        Returns true if this query could refer to a postcode. This requires at
        least 4 digits, followed by at most two non-digits.
        """
        if self._token_count == 1:
            cijfers = self._tokens[0]
            return (
                len(cijfers) == 4
                and cijfers.isdigit()
            )

        elif self._token_count == 2:
            cijfers, letters = self._tokens[0:2]
            return (
                len(cijfers) == 4
                and cijfers.isdigit()
                and len(letters) == 2
                and not letters.isdigit()
            )

        return False

    def get_postcode(self):
        """
        Assuming this query refers to a postcode, this returns the postcode
        query.
        """
        assert self.is_postcode_prefix()
        return " ".join(self._tokens[:2])

    def is_postcode_huisnummer_prefix(self) -> bool:
        """
        Returns true if this query could refer to postcode/huisnummer
        combination. This requires a full postcode followed by a huisnummer.
        """
        if self._token_count < 3:
            return False

        cijfers, letters, huisnummer = self._tokens[:3]
        return (
            len(cijfers) == 4
            and cijfers.isdigit()
            and len(letters) == 2
            and not letters.isdigit()
            and huisnummer.isdigit()
        )

    def _contruct_huisnummer_toevoeging(self, start_index) -> str:
        """
        Constructs a huisnummer/toevoeging combination from the tokens
        starting at start_index.
        """
        result = []
        for token in self._tokens[start_index:]:
            if token.isdigit():
                result.append(token)
            else:
                result.extend(token)

        return " ".join(result)

    def get_postcode_huisnummer_toevoeging(self) -> (str, int, str):
        """
        Assuming that this query represents a postcode_huisnummer, this
        returns the postcode, the huisnummer and the huisnummer + toevoeging.
        """
        assert self.is_postcode_huisnummer_prefix()

        huisnummer = int(self._tokens[2])
        huisnummer_toevoeging = self._contruct_huisnummer_toevoeging(2)
        postcode = "".join(self._tokens[:2])
        return postcode, huisnummer, huisnummer_toevoeging

    def is_straatnaam_huisnummer_prefix(self) -> bool:
        """
        Returns true if this query could refer to straatnaam/huisnummer
        combination.
        """
        if self._token_count < 2:
            return False

        if self._tokens[0].isdigit() and len(self._tokens[0]) > 1:
            return False

        return self._huisnummer_index is not None

    def get_straatnaam_huisnummer_toevoeging(self) -> (str, int, str):
        """
        Assuming that this query represents a straat_huisnummer, this returns
        the straatnaam, the huisnummer and the huisnummer + toevoeging.
        """
        assert self.is_straatnaam_huisnummer_prefix()

        straat = " ".join(self._tokens[:self._huisnummer_index])
        huisnummer = int(self._tokens[self._huisnummer_index])
        huisnummer_toevoeging = \
            self._contruct_huisnummer_toevoeging(self._huisnummer_index)

        return straat, huisnummer, huisnummer_toevoeging

    def get_straatnaam(self) -> str:
        """
        Assuming that this query represents a straatnaam, this returns the
        straatnaam.
        """
        return " ".join(self._tokens)
