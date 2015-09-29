import elasticsearch_dsl as es

kadastrale_aanduiding = es.analyzer('kadastrale_aanduiding', tokenizer='keyword', filter=['standard', 'lowercase'])
adres = es.analyzer('adres', tokenizer='keyword', filter=['standard', 'lowercase', 'asciifolding'])

naam = es.analyzer('naam', tokenizer='keyword', filter=['standard', 'lowercase', 'asciifolding'])