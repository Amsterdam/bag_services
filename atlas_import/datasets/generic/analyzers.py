import elasticsearch_dsl as es
from elasticsearch_dsl import analysis

synonym_filter = analysis.token_filter(
    'synonyms',
    type='synonym',
    synonyms=[
        '1e=>eerste',
        '2e=>tweede',
        '3e=>derde',
        '4e=>vierde',
    ])

stripper = analysis.char_filter(
    'stripper',
    type='mapping',
    mappings=[
        "-=>",      # strip '-'
        ".=>' '",   # change '.' to separator
    ])

kadastrale_aanduiding = es.analyzer(
    'kadastrale_aanduiding',
    tokenizer='keyword'
    , filter=['standard', 'lowercase'])

adres = es.analyzer(
    'adres',
    tokenizer='standard',
    filter=['standard', 'lowercase', 'asciifolding', synonym_filter],
    char_filter=[stripper],
)

naam = es.analyzer(
    'naam',
    tokenizer='standard',
    filter=['standard', 'lowercase', 'asciifolding', synonym_filter],
    char_filter=[stripper]
)
