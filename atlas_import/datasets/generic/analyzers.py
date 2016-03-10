import elasticsearch_dsl as es
from elasticsearch_dsl import analysis, tokenizer


orderings = {
    'openbare_ruimte': 10,
    'kadastraal_subject': 25,
    'adres': 50,
    'kadastraal_object': 100
}


####################################
#            Filters               #
####################################
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

naam_stripper = analysis.char_filter(
    'naam_stripper',
    type='mapping',
    mappings=[
        "-=>' '",   # change '-' to separator
        ".=>' '",   # change '.' to separator
    ]
)

# {
#     "filter": {
#         "autocomplete_filter": {
#             "type":     "edge_ngram",
#             "min_gram": 1,
#             "max_gram": 20
#         }
#     }
# }
autocomplete_filter = analysis.token_filter(
    'autocomplete_filter',
    type='edge_ngram',
    min_gram=3,
    max_gram=10
)
####################################
#           Analyzers              #
####################################

kadastrale_aanduiding = es.analyzer(
    'kadastrale_aanduiding',
    tokenizer='keyword',
    filter=['standard', 'lowercase']
)


adres = es.analyzer(
    'adres',
    tokenizer='standard',
    filter=['standard', 'lowercase', 'asciifolding', synonym_filter],
    char_filter=[adres_split, huisnummer_generate],
)


naam = es.analyzer(
    'naam',
    tokenizer='standard',
    filter=['standard', 'lowercase', 'asciifolding', synonym_filter],
    char_filter=[naam_stripper],
)


postcode_ng = es.analyzer(
    'postcode_ng',
    tokenizer=tokenizer('postcode_ngram', 'nGram', min_gram=2, max_gram=4, token_chars=['letter', 'digit']),
    filter=['standard', 'lowercase'],
)

postcode = es.analyzer(
    'postcode',
    tokenizer=tokenizer('postcode_keyword', 'keyword', token_chars=['letter', 'digit']),
    filter=['standard', 'lowercase'],
)

huisnummer = es.analyzer(
    'huisnummer',
    tokenizer='whitespace',
    filter=['lowercase', huisnummer_expand],
    char_filter=[adres_split, huisnummer_generate],
)


subtype = es.analyzer(
    'subtype',
    tokenizer='keyword',
    filter=['standard', 'lowercase'],
)

# {
#     "analyzer": {
#         "autocomplete": {
#             "type":      "custom",
#             "tokenizer": "standard",
#             "filter": [
#                 "lowercase",
#                 "autocomplete_filter"
#             ]
#         }
#     }
# }
autocomplete = es.analyzer(
    'autocomplete',
    tokenizer='standard',
    filter=['lowercase', autocomplete_filter]
)
