test = "CriteriaAlternatives\oile0.txt"
test2 = "xxx.txt"
hehe = open(test2,'w')
with open(test) as of:
    ff = of.read()
    xx = ff.split()
    for y in (xx[x:x+4] for x in range(0,len(xx),4)):
       hehe.write("%s\n",y)
