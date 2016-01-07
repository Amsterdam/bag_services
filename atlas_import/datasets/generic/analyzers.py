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
    ])

postcode_ngram = analysis.NGramTokenizer(
    name='postcode_ngram',
    min_gram=2,
    max_gram=4,
    token_chars=['letter', 'digit'])

adres_stripper = analysis.char_filter(
    'adres_stripper',
    type='mapping',
    mappings=[
        "-=>' '",      # strip '-'
        ".=>' '",   # change '.' to separator
    ])


naam_stripper = analysis.char_filter(
    'naam_stripper',
    type='mapping',
    mappings=[
        "-=>' '",   # change '-' to separator
        ".=>' '",   # change '.' to separator
    ])


#postcode_stripper = analysis.char_filter(
#    'postcode_stripper',
#    type='pattern_replace',
#    pattern=r'[\s\-]',        # strip whitespace and '-'
#    replacement='',
#)

kadastrale_aanduiding = es.analyzer(
    'kadastrale_aanduiding',
    tokenizer='keyword',
    filter=['standard', 'lowercase'])


adres = es.analyzer(
    'adres',
    tokenizer='standard',
    filter=['standard', 'lowercase', 'asciifolding', synonym_filter],
    char_filter=[adres_stripper],
    type='custom'
)

naam = es.analyzer(
    'naam',
    tokenizer='standard',
    filter=['standard', 'lowercase', 'asciifolding', synonym_filter],
    char_filter=[naam_stripper],
)

postcode = es.analyzer(
    'postcode',
    type='custom',
    #tokenizer='keyword',
    tokenizer=postcode_ngram,
    filter=['standard', 'lowercase'],
    #char_filter=[postcode_stripper],
)

subtype = es.analyzer(
    'subtype',
    tokenizer='keyword',
    filter=['standard', 'lowercase'],
    char_filter=[adres_stripper],
)


