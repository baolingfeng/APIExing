vocab = []
with open('w2v_pandas.txt.vcb', 'r') as f:
    for line in f:
        line = line.strip()
        vocab.append(line.split()[0])
print len(vocab)

compound = {}
with open('./w2v_pandas.txt-100/optimized_kmeans_pp.kmc', 'r') as f:
    for line in f:
        line = line.strip().split('\t')
        compound.setdefault(line[1], []).append(line[0])
        #try:
        #    compound[line[1]].append(line[0])
        #except KeyError:
        #    compound[line[1]] = [line[0]]
print len(compound)

with open('./w2v_pandas.txt-300/optimized_kmeans_pp.kmc', 'r') as f:
    for line in f:
        line = line.strip().split('\t')
        compound.setdefault(line[1], []).append(line[0])
with open('./w2v_pandas.txt-500/optimized_kmeans_pp.kmc', 'r') as f:
    for line in f:
        line = line.strip().split('\t')
        compound.setdefault(line[1], []).append(line[0])
with open('./w2v_pandas.txt-800/optimized_kmeans_pp.kmc', 'r') as f:
    for line in f:
        line = line.strip().split('\t')
        compound.setdefault(line[1], []).append(line[0])
with open('./w2v_pandas.txt-1000/optimized_kmeans_pp.kmc', 'r') as f:
    for line in f:
        line = line.strip().split('\t')
        compound.setdefault(line[1], []).append(line[0])


import json
with open('kmcluster_pandas.txt', 'w') as fout:
    for key, value in compound.items():
        sout = key
        for x in value:
            sout = sout + '\t' + x
        sout += '\n'
        fout.write(sout)
