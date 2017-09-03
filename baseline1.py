import sys, re

api_neg = []
api_pos = []

with open('./apidoc/pd-np-mpl-ambAPI.txt', 'r') as neg:
    for line in neg:
        if line != '\n':
            line = line.strip()
            #line = line.lower()
            api_neg.append(line)

# np
#with open('../../numpy/ambiguousAPI.txt', 'r') as neg:
#    for line in neg:
#        if line != '\n':
#            line = line.strip()
#            api_neg.append(line)

# mpl
#with open('../../matplotlib/ambiguousAPI.txt', 'r') as neg:
#    for line in neg:
#        if line != '\n':
#            line = line.strip()
#            api_neg.append(line)

# pd
#with open('../apidoc/ambiguousAPI.txt', 'r') as neg:
#    for line in neg:
#        if line != '\n':
#            line = line.strip()
#            api_neg.append(line)

with open('./apidoc/pd-np-mpl-remove.txt', 'r') as pos:
    for line in pos:
        if line != '\n':
            line = line.strip()
            #line = line.lower()
            api_pos.append(line)


fout = open(sys.argv[2], 'w')

with open(sys.argv[1], 'r') as f:
	for line in f:
		if line != '\n':
			line = line.strip()
			word = line.split()[0]
                        if word in api_neg or line in api_pos: #or word.endswith("()"):
				outline = line + '\tB-API\n'
				fout.write(outline)
			elif re.match(r'[a-zA-Z_]*\.[a-z_]+.*', word):
			#elif any(word in api for api in api_pos):
				outline = line + '\tB-API\n'
				fout.write(outline)
			else:
				outline = line + '\tO\n'
				fout.write(outline)
		else:
			fout.write(line)
