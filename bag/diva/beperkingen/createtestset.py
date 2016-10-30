infn = 'wpb_belemmering_50.dat'

def createBelPerc(ids):
    basefn = 'wpb_belemmering_perceel'
    infile = open(basefn + '.dat','r')
    outfile = open(basefn + '_50.dat','w')
    for line in infile:
        items = line.strip().split(';')
        if items[5] in ids:
            outfile.write(line)
    infile.close()
    outfile.close()

def createBrondoc(nrs):
    basefn = 'wpb_brondocument'
    infile = open(basefn + '.dat','r')
    outfile = open(basefn + '_50.dat','w')
    for line in infile:
        items = line.strip().split(';')
        if items[0] in nrs:
            outfile.write(line)
    infile.close()
    outfile.close()


infile = open(infn,'r')
ids = []
nrs = []
for line in infile:
    #print line
    items = line.strip().split(';')
    #print items[0], items[1]
    ids.append(items[0])
    nrs.append(items[1])
infile.close()

print(len(ids), len(nrs))
print(ids)
print(nrs)

createBelPerc(ids)
createBrondoc(nrs)

