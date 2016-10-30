def get_aanduiding(gemeente, sectie, perceelnummer, objectindex_letter, objectindex):
    return '{0}{1}{2:0>5}{3}{4:0>4}'.format(gemeente, sectie, perceelnummer, objectindex_letter, objectindex)

def get_aanduiding_spaties(gemeente, sectie, perceelnummer, objectindex_letter, objectindex):
    return '{0} {1} {2:0>5} {3} {4:0>4}'.format(gemeente, sectie, perceelnummer, objectindex_letter, objectindex)
