import csv
import io

data = []
roots = set()
mapping = {}
        
treeFile = open('cdtree.csv', 'r')
next(treeFile)
treeReader = csv.reader(treeFile)
for fields in treeReader:
    p = int(fields[1])
    #print(p)
    c = int(fields[2])
    #print(c)
    data.append(tuple([p,c]))
#print(data)

for parent,child in data:
    leaf = mapping.get(child, None)
    if leaf is None:
        leaf = {}
        mapping[child] = leaf
    else: roots.discard(child)
    parentitem = mapping.get(parent, None)
    if parentitem is None:
        mapping[parent] = {child:leaf}
        roots.add(parent)
    else: parentitem[child] = leaf

tree = {id: mapping[id] for id in sorted(roots)}
outfile = open('file.txt', 'w')
outfile.write(str(tree))