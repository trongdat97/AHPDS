import os
import numpy as np
from ortools.linear_solver import pywraplp
from more_itertools import powerset

criteriaList = list()
goalList = list()
for filename in os.listdir("CriteriaAlternatives"):
    criteriaElement = dict()
    criteriaElement['name'] = filename.replace('.txt','')
    criteriaElement[filename] = np.loadtxt(fname= (os.getcwd()+'\\CriteriaAlternatives\\' + filename))
    criteriaList.append(criteriaElement) 

for filename in os.listdir("CriteriaVersusGoal"): 
    goalElement = dict()
    goalElement['name'] = filename.replace('.txt','')
    goalElement[filename] = np.loadtxt(fname= (os.getcwd()+'\\CriteriaVersusGoal\\' + filename))
    goalList.append(goalElement)

fhand = open('Alternatives.txt')
for line in fhand: 
    listOfAlternatives =(line.split(','))
num = len(listOfAlternatives)
def frequencyCalculation(nlist):
    for i in nlist:
        l = len(i[i["name"]+".txt"])
        newarray = np.zeros(l)
        nrowSum = i[i["name"]+".txt"].sum()
        for j in range(l):
            newarray[j] = i[i["name"]+".txt"][j] / nrowSum
        i["Frequency"] = newarray
    return nlist
goalList = frequencyCalculation(goalList)

criteriaList = frequencyCalculation(criteriaList)



def BelAndPlCalculation(nlist):
    for i in nlist:
        l = len(i[i["name"]+".txt"])
        belArray = np.zeros(l)
        plArray = np.zeros(l)
        index = list(powerset(np.arange(0, int(np.log2(l+1)))))
        index.pop(0)
        mydict = dict()
        for j in range(len(index)):
            mydict[index[j]] = i["Frequency"][j]
        for j in range(len(index)):
            newset = list(powerset(index[j]))
            newset.pop(0)
            sum = 0
            for k in range(len(newset)):
                sum+=mydict[newset[k]]
            belArray[j] = sum
        for j in range(len(index)):
            sum = 0
            for k in range(len(index)):
                if len(set(index[j]).intersection(set(index[k])))>0:
                    sum += mydict[index[k]]
            plArray[j] = sum
        i["BelArray"] = belArray
        i["PlArray"] = plArray
    return nlist

goalList = BelAndPlCalculation(goalList)

criteriaList = BelAndPlCalculation(criteriaList)

variArray = np.zeros(int(np.log2(len(goalList[0]["Frequency"])+1)))

for i in range(len(variArray)):
    variArray[i] = 97 + i

solver = pywraplp.Solver.CreateSolver("GLOP")
x = solver.NumVar(0, solver.infinity(), 'x')
y = solver.NumVar(0, solver.infinity(), 'y')

# print('Number of constraints =', solver.NumConstraints())
for i in goalList:
    solver.Add(x>=i["BelArray"][0])
    solver.Add(x<=i["PlArray"][0])
    solver.Add(y>=i["BelArray"][1])
    solver.Add(y<=i["PlArray"][1])
    solver.Add(x+y>=i["BelArray"][2])
    solver.Add(x+y<=i["PlArray"][2])
status = solver.Solve()

compareMatrix = np.zeros((2, len(criteriaList[0]["Frequency"])))

for i in range(compareMatrix.shape[1]):
    compareMatrix[0][i] = x.solution_value() * criteriaList[0]["BelArray"][i] + y.solution_value() * criteriaList[1]["BelArray"][i]
    compareMatrix[1][i] = x.solution_value() * criteriaList[0]["PlArray"][i] + y.solution_value() * criteriaList[1]["PlArray"][i]

solver2 = pywraplp.Solver.CreateSolver("GLOP")
a = solver2.NumVar(0, solver2.infinity(), 'a')
solver2.Add(a>=0)
solver2.Add(a<=1)
maxArray= []
for i in range(num):
    solver2.Maximize(a * compareMatrix[0][i] + (1-a)* compareMatrix[1][i])
    solver2.Solve()
    maxArray.append(solver2.Objective().Value())

result = list()

for i in range(num):
    resultElement = dict()
    resultElement[listOfAlternatives[i]] = maxArray[i]
    result.append(resultElement)
print("Compare matrix between all alternatives: ", result )
print("The best Alternatives is: ", listOfAlternatives[maxArray.index(max(maxArray))])


