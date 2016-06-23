"""
A collection of custom elastic search filters and analyzers
that are used throughout.
"""

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

# Replaces the number street shortening with the actual word
synonym_filter = analysis.token_filter(
    'synonyms',
    type='synonym',
    synonyms=[
        '1e, eerste => 1e, eerste',
        '2e, tweede => 2e, tweede',
        '3e, derde  => 3e, derde',
        '4e, vierde => 4e, vierde',
    ]
)


huisnummer_expand = analysis.token_filter(
    'huisnummer_expand',
    type='word_delimiter',
    generate_numer_parts=True,
    preserve_original=True
)


# Change dash and dot to space
naam_stripper = analysis.char_filter(
    'naam_stripper',
    type='mapping',
    mappings=[
        "-=>' '",  # change '-' to separator
        ".=>' '",  # change '.' to separator
        "/=>' '",  # change '/' to separator
    ]
)

# normalizes ., -, / to space from text
divider_normalizer = analysis.token_filter(
    'divider_normalizer',
    type='pattern_replace',
    pattern='(str\.|\/|-)',
    replacement=' '
)


# Removes ., -, / and space from text
divider_stripper = analysis.token_filter(
    'divider_stripper',
    type='pattern_replace',
    pattern='(str\.|\/|-|\.| )',
    replacement=''
)

# Remove white spaces from the text
whitespace_stripper = analysis.token_filter(
    'whitespace_stripper',
    type='pattern_replace',
    pattern=' ',
    replacement=''
)

ngram_filter = analysis.token_filter(
    'ngram_filter',
    type='ngram',
    min_gram=3,
    max_gram=15
)

# Create edge ngram filtering to postcode
edge_ngram_filter = analysis.token_filter(
    'edge_ngram_filter',
    type='edge_ngram',
    min_gram=1,
    max_gram=15
)

# Creating ngram filtering to kadastral objects
kadaster_object_aanduiding = analysis.token_filter(
    'kad_obj_aanduiding_filter',
    type='ngram',
    min_gram=4,
    max_gram=16
)

####################################
#           Analyzers              #
####################################

bouwblok = es.analyzer(
    'bouwblok',
    tokenizer=tokenizer(
        'edge_ngram_filter',
        type='edge_ngram',
        min_gram=2, max_gram=4,
        token_chars=["letter", "digit"]),
    filter=['lowercase', divider_stripper],
    # char_filter=[divider_stripper]
)

adres = es.analyzer(
    'adres',
    tokenizer='standard',
    filter=['lowercase', 'asciifolding', synonym_filter],
    # filter=['lowercase', 'asciifolding'],
    char_filter=[naam_stripper],
)

straatnaam = es.analyzer(
    'straatnaam',
    tokenizer='standard',
    filter=['lowercase', 'asciifolding', divider_normalizer],
)

naam = es.analyzer(
    'naam',
    tokenizer='standard',
    # filter=['standard', 'lowercase', 'asciifolding', synonym_filter],
    filter=['standard', 'lowercase', 'asciifolding'],
    char_filter=[naam_stripper],
)

postcode_ng = es.analyzer(
    'postcode_ng',
    tokenizer=tokenizer(
        'postcode_ngram', 'nGram',
        min_gram=2, max_gram=4,
        token_chars=['letter', 'digit']),
    filter=['lowercase'],
)

postcode = es.analyzer(
    'postcode',
    tokenizer=tokenizer(
        'postcode_keyword', 'keyword', token_chars=['letter', 'digit']),
    filter=['lowercase', whitespace_stripper],
)

huisnummer = es.analyzer(
    'huisnummer',
    tokenizer='whitespace',
    filter=['lowercase', huisnummer_expand],
    char_filter=[naam_stripper],
)

subtype = es.analyzer(
    'subtype',
    tokenizer='keyword',
    filter=['lowercase'],
)

autocomplete = es.analyzer(
    'autocomplete',
    tokenizer='standard',
    filter=['lowercase', edge_ngram_filter]
)

ngram = es.analyzer(
    'ngram_analyzer',
    tokenizer='standard',
    filter=['lowercase', ngram_filter]
)


toevoeging = es.analyzer(
    'toevoeging_analyzer',
    tokenizer='keyword',
    filter=['lowercase', edge_ngram_filter],
    char_filter=[naam_stripper]
)

kad_obj_aanduiding = es.analyzer(
    'kad_obj_aanduiding',
    tokenizer=tokenizer(
        'kadobj_token', 'nGram',
        min_gram=1, max_gram=16,
        token_chars=['letter', 'digit']),
    filter=['lowercase']
)

kad_sbj_naam = es.analyzer(
    'kad_sbj_naam',
    tokenizer=tokenizer(
        'kadobj_token', 'nGram',
        min_gram=3, max_gram=16,
        token_chars=['letter', 'digit']),
    filter=['lowercase']
)

kad_obj_aanduiding_keyword = es.analyzer(
    'kad_obj_aanduiding_keyword',
    tokenizer=tokenizer(
        'kadobj_keyword', 'keyword',
        token_chars=['letter', 'digit']),
    filter=['lowercase']
)
