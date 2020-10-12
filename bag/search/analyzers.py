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
# https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-mapping-charfilter.html
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


# Change dash and dot and slash to space
# When this is done with pattern_replace this gives problems when searching for
# zijkanaal h 2
# It is also not needed to map quotes.
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
    pattern=r'(str\.|\/|-)',
    replacement=' '
)


# Removes ., -, / and space from text
divider_stripper = analysis.token_filter(
    'divider_stripper',
    type='pattern_replace',
    pattern=r'(str\.|\/|-|\.| )',
    replacement=''
)

# Remove white spaces from the text
whitespace_stripper = analysis.token_filter(
    'whitespace_stripper',
    type='pattern_replace',
    pattern=' ',
    replacement=''
)

# Create edge edge_ngram filtering to postcode
edge_ngram_filter = analysis.token_filter(
    'edge_ngram_filter',
    type='edge_ngram',
    min_gram=1,
    max_gram=20,
)

# Creating ngram filtering to kadastral objects
kadaster_object_aanduiding = analysis.token_filter(
    'kad_obj_aanduiding_filter',
    type='edge_ngram',
    min_gram=1,
    max_gram=6,
)

lowercase = analysis.normalizer(
    'lowercase_keyword',
    filter=['lowercase']
)

strip_zero = analysis.CustomCharFilter(
    "strip_zero",
    builtin_type="pattern_replace",
    pattern="^0+(.*)",
    replacement="$1"
)

####################################
#           Analyzers              #
####################################

bouwblokid = es.analyzer(
    'bouwbloknummer',
    tokenizer=tokenizer(
        'bouwbloktokens',
        'edge_ngram',
        min_gram=1, max_gram=4,
        token_chars=["letter", "digit"]),
    filter=['lowercase', divider_stripper],
)

adres = es.analyzer(
    'adres',
    tokenizer='standard',
    filter=['lowercase', 'asciifolding', synonym_filter],
    # fi`lter=['lowercase', 'asciifolding'],
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

postcode = es.analyzer(
    'postcode',
    tokenizer=tokenizer(
        'postcode', 'edge_ngram',
        min_gram=1, max_gram=6,
        token_chars=['letter', 'digit']),
    filter=[
        'lowercase',
        whitespace_stripper,
    ],
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

adres1 = es.analyzer(
    'adres1',
    tokenizer='standard',
    filter=['standard', 'lowercase', 'asciifolding', synonym_filter, 'shingle'],
    token_separator=''
)

straat_no_ws = es.analyzer(
    'straat_no_ws',
    tokenizer='keyword',
    filter=['lowercase', 'asciifolding', synonym_filter, whitespace_stripper],
)

autocomplete = es.analyzer(
    'autocomplete',
    tokenizer='standard',
    filter=['lowercase', edge_ngram_filter]
)


toevoeging = es.analyzer(
    'toevoeging_analyzer',
    tokenizer='keyword',
    filter=['lowercase', edge_ngram_filter],
    token_chars=['letter', 'digit'],
    char_filter=[
        naam_stripper,
    ]
)


kad_obj_aanduiding = es.analyzer(
    'kad_obj_aanduiding',
    tokenizer=tokenizer(
        'kadobj_token',
        type='edge_ngram',
        min_gram=1, max_gram=16,
        token_chars=['letter', 'digit']),
    filter=['lowercase']
)


kad_obj_nummer = es.analyzer(
    'kad_obj_nummer',
    tokenizer=tokenizer(
        'kadobj_nummer',
        type='edge_ngram',
        min_gram=1, max_gram=5
    ),
)


kad_sbj_naam = es.analyzer(
    'kad_sbj_naam',
    tokenizer=tokenizer(
        'kadobj_token', 'nGram',
        min_gram=3, max_gram=4,
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


nozero = es.analyzer(
    'nozero',
    tokenizer='standard',
    filter=[edge_ngram_filter],
    char_filter=[strip_zero])
