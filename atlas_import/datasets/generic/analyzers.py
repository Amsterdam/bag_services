import elasticsearch_dsl as es
from elasticsearch_dsl import analysis


orderings = dict(
    openbare_ruimte=10,
    kadastraal_subject=25,
    adres=50,
    kadastraal_object=100,
)


synonym_filter = analysis.token_filter(
    'synonyms',
    type='synonym',
    synonyms=[
        '1e=>eerste',
        '2e=>tweede',
        '3e=>derde',
        '4e=>vierde',
    ]
)


huisnummer_generate = analysis.char_filter(
    'huisnummer_expand',
    type='pattern_replace',
    pattern='(\d+)',
    replacement="""
        $1-1 $1- $1-2 $1-3
        $1a $1b $1a-1 $1b-1 $1-a $1-b
        $1b 1-b
        $1c 1-c
        $1d 1-d
        $1e 1-e
        $1f 1-f
        $1g 1-g
        $1h 1-h
        $1i 1-i
        $1j 1-j
        $1k 1-k
        $1l 1-l
        $1m 1-m
        $1n 1-n
        $1o 1-o
    """
)


huisnummer_expand = analysis.token_filter(
    'huisnummer_expand',
    type='word_delimiter',
    generate_numer_parts=True,
    preserve_original=True
)


adres_split = analysis.char_filter(
    'adres_split',
    type='mapping',
    mappings=[
        "-=>' '",   # strip '-'
        ".=>' '",   # change '.' to separator
    ]
)


postcode_ngram = analysis.NGramTokenizer(
    name='postcode_ngram',
    min_gram=4,
    max_gram=6,
    token_chars=['letter', 'digit']
)


toevoeing_ngram = analysis.NGramTokenizer(
    name='toevoeing_ngram',
    min_gram=1,
    max_gram=4,
    token_chars=['letter', 'digit']
)


naam_stripper = analysis.char_filter(
    'naam_stripper',
    type='mapping',
    mappings=[
        "-=>' '",   # change '-' to separator
        ".=>' '",   # change '.' to separator
    ]
)
postcode_split = analysis.char_filter(
    'naam_stripper',
    type='mapping',
    mappings=[
        "-=>' '",   # change '-' to separator
        ".=>' '",   # change '.' to separator
    ]
)


kadastrale_aanduiding = es.analyzer(
    'kadastrale_aanduiding',
    tokenizer='keyword',
    filter=['standard', 'lowercase']
)


adres = es.analyzer(
    'adres',
    tokenizer='standard',
    filter=['standard', 'lowercase', 'asciifolding', synonym_filter],
    char_filter=[
        adres_split,
        huisnummer_generate
    ],
)


naam = es.analyzer(
    'naam',
    tokenizer='standard',
    filter=['standard', 'lowercase', 'asciifolding', synonym_filter],
    char_filter=[naam_stripper],
)


postcode = es.analyzer(
    'postcode',
    # tokenizer='keyword',
    tokenizer=postcode_ngram,
    filter=['standard', 'lowercase'],
    char_filter=[postcode_split],
)

toevoeging = es.analyzer(
    'toevoeging',
    tokenizer='standard',
    filter=['standard', 'lowercase'],
    char_filter=[naam_stripper]
)


huisnummer = es.analyzer(
    'huisnummer',
    tokenizer='whitespace',
    filter=['lowercase', huisnummer_expand],
    # token_filter=[huisnummer_expand],
    char_filter=[adres_split, huisnummer_generate],
)


subtype = es.analyzer(
    'subtype',
    tokenizer='keyword',
    filter=['standard', 'lowercase'],
)
