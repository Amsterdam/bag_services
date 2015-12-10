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

adres_stripper = analysis.char_filter(
    'adres_stripper',
    type='mapping',
    mappings=[
        "-=>",      # strip '-'
        ".=>' '",   # change '.' to separator
    ])

postcode_stripper = analysis.char_filter(
    'postcode_stripper',
    type='pattern_replace',
    pattern=r'[\s\-]',        # strip whitespace and '-'
    replacement='',
)

kadastrale_aanduiding = es.analyzer(
    'kadastrale_aanduiding',
    tokenizer='keyword',
    filter=['standard', 'lowercase'])

adres = es.analyzer(
    'adres',
    tokenizer='standard',
    filter=['standard', 'lowercase', 'asciifolding', synonym_filter],
    char_filter=[adres_stripper],
)

naam = es.analyzer(
    'naam',
    tokenizer='standard',
    filter=['standard', 'lowercase', 'asciifolding', synonym_filter],
    char_filter=[adres_stripper],
)

postcode = es.analyzer(
    'postcode',
    tokenizer='keyword',
    filter=['standard', 'lowercase'],
    char_filter=[postcode_stripper],
)
