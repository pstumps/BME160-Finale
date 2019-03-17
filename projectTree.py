import csv
import io

#from anytree import Node, RenderTree

data = []
roots = set()
mapping = {}
        
treeFile = open('cdtree.csv', 'r')
nameFile = open('HexaPropsAssay.csv', 'r')
next(nameFile)
next(treeFile)
nameList = []
childList = []
parentList = []
treeReader = csv.reader(treeFile, delimiter = ",")
#nameReader = csv.reader(nameFile, delimiter = ",")
for fields in csv.reader(treeFile, delimiter = ","):
    nodeInt = int(fields[2]) +1
    childList.append(nodeInt)
childList.sort()
print(childList)
for names in csv.reader(nameFile, delimiter = ","):
    nameList.append(names[0])
leafDictionary = dict(zip(childList, nameList))
for key, value in sorted(leafDictionary.items(), key = lambda x:x[0] ):
    print(key, value)

treeFile.seek(0)
next(treeFile)

nodeList = []

for fields in treeReader:
    p = int(fields[1])
    #print(p)
    c = int(fields[2])+1
    #node = 
    data.append(tuple([p,c]))



for parent,child in data:
    print(child)
    leaf = mapping.get(child, None)
    if leaf is None:
        leaf = {}
        mapping[child] = leaf
    elif type(leaf) is int:
        if int(leaf) <= 839:
            leaf = leafDictionary[child]
    else:
        roots.discard(child)
    parentitem = mapping.get(parent, None)
    if parentitem is None:
        mapping[parent] = {child:leaf}
        roots.add(parent)
    else: parentitem[child] = leaf

tree = {id: mapping[id] for id in sorted(roots)}
outfile = open('file.txt', 'w')
outfile.write(str(tree))