import itertools
import random
import gurobipy as gp
from gurobipy import GRB
import os

#task class
#ID: the task id
#cras: array of cars
class task:
    ID = 0
    cars = []

    def __repr__(self):
        return "task:" + str(self.ID) + " cars:" + str(self.cars) + "\n"

    def __str__(self):
        return "task:" + str(self.ID) + " cars:" + str(self.cars) + "\n"

    def __init__(self, idd, cars):
        self.ID = idd
        self.cars = cars

    def __eq__(self, obj):
        return self.ID == obj.ID and self.cars == obj.cars

    def __hash__(self):
        return hash((self.ID, tuple(self.cars)))

#parameters
infNum = 1000
S = [0, 1, 2, 3]  # set of servers
C = [0, 1]  # set of cars
K = [1, 2]
Ps = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11]]  # Ps[s] ==> set of processing unit of server s
pFromS = [0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3]  # pFromS[p] processing unit p belongs to which server
P = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
V = [0, 1, 2]  # set of tasks
VT = [1, 0, 1]
Pc = [[0, 1, 2, 6, 7, 8, 9, 10, 11],
      [3, 4, 5, 6, 7, 8, 9, 10, 11]]  # Pc[c] ==> set of processing units that tasks of car c can be run on
Trelease = [[0, 0.1, 0.2], [0, 0.1, 0.2]]  # Trelease[c][i] ==>  release time of task i from car c
Tdue = [[40, 80, 170], [40, 80, 170]]  # Tdue[c][i] ==> deadline of task i from car c
E = [(0, 1), (1, 2)]  # set of edges
Isuc = [[1, 2], [2], []]  # Ipr[i]: succor of task i
Ipr = [0, 0, 2]  # Ipr[i] the last aggregable node before task i
ET = {}  # ET[p,c,i]: execution time of task i aggregated from c(NUM) cars on processing unit p
for p, c, i in itertools.product(P, K, V):
    if pFromS[p] <= 1:
        ET[p, c, i] = 3/(c+1)

    if pFromS[p] == 2:
        ET[p, c, i] = 2/(c+1)

    if pFromS[p] == 3:
        ET[p, c, i] = 2/(c+1)
CT = {}  # CT[p,q,c,c',i,j]communication delay between task i and j of car c and task i is aggregated
# from c_ cars

for p, q, c, c_, i, j in itertools.product(P, P, C, C, V, V):
    if i == j or p == q:
        CT[p, q, c, c_, i, j] = 0
        continue

    if pFromS[p] == pFromS[q]:
        CT[p, q, c, c_, i, j] = 1
        continue
    CT[p, q, c, c_, i, j] = (pFromS[p] - pFromS[q]) / (c+1)
#=========================Generating Test Scenario===========
taskDependency = "VGG-19"
# taskDependency = "Xception"
# taskDependency = "PilotNet"
numberOfCars = random.randint(2, 10)
numberOfCars = 2
C = [i for i in range(numberOfCars)]
S = [i for i in range(numberOfCars)]
S.append(numberOfCars)
S.append(numberOfCars+1)
S = [0,1,2]
K = [i+1 for i in range(numberOfCars)]
Ps = []
temp = 0
numberOfProcessingUnitsOfCars = 3
numberOfProcessingUnitsOfEdge = 5
numberOfProcessingUnitsOfCloud = 5
pFromS = [0 for l in range(numberOfProcessingUnitsOfCars*numberOfCars+numberOfProcessingUnitsOfEdge+numberOfProcessingUnitsOfCloud)]
for i in C:
    tempArr = [temp+k for k in range(numberOfProcessingUnitsOfCars)]
    for j in range(temp,temp+numberOfProcessingUnitsOfCars):
        pFromS[j] = i
    temp = (i+1)*numberOfProcessingUnitsOfCars
    Ps.append(tempArr)
tempArr = [temp+i for i in range(numberOfProcessingUnitsOfEdge)]
Ps.append(tempArr)
for j in range(temp,temp+numberOfProcessingUnitsOfEdge):
    pFromS[j] = numberOfCars
temp += numberOfProcessingUnitsOfEdge
tempArr = [temp+i for i in range(numberOfProcessingUnitsOfCloud)]
for j in range(temp,temp+numberOfProcessingUnitsOfCloud):
    pFromS[j] = numberOfCars + 1
Ps.append(tempArr)
print(Ps)
print(numberOfCars)
P = [l for l in range(numberOfProcessingUnitsOfCars*numberOfCars+numberOfProcessingUnitsOfEdge+numberOfProcessingUnitsOfCloud)]
Pc = []
for i in C:
    Pc.append(Ps[i]+Ps[numberOfCars]+Ps[numberOfCars+1])
#=========================VGG-19===========================
if taskDependency == "VGG-19":
    V = [i for i in range(25)]
    VT = [0 for i in range(25)]
    VT[0] = 1
    for i in range(1,24):
        VT[i] = int(random.randint(0,5)/5)
    VT[24] = 1
    E = []
    for i in range(0,24):
        E.append((i,i+1))
    Isuc = []
    for i in range(25):
        Isuc.append([j for j in range(i+1,25)])
    Ipr = []
    lastAggregableNode = 0
    for i in range(25):
        if VT[i] == 1:
            lastAggregableNode = i
        Ipr.append(lastAggregableNode)
    #Ececution time
    taskComputationRequirement = [random.randint(5,15)/10 for i in range(25)] #this is for paper
    # taskComputationRequirement = [random.randint(5,15)*4*3*5 for i in range(25)]
    computationCapability = [1 for i in range(numberOfCars * numberOfProcessingUnitsOfCars)]
    computationCapability += [random.randint(1,5)*5 for i in range(numberOfProcessingUnitsOfEdge + numberOfProcessingUnitsOfCloud)] #this is for paper
    # computationCapability += [random.randint(1,5) for i in range(numberOfProcessingUnitsOfEdge + numberOfProcessingUnitsOfCloud)]
    for p, c, i in itertools.product(P, K, V):
        if c == 1:
            # ET[p,c,i] = int((taskComputationRequirement[i] / computationCapability[p])*100) + 1
            ET[p,c,i] = (taskComputationRequirement[i] / computationCapability[p])
            continue
        # ET[p, c, i] = int(((taskComputationRequirement[i] / computationCapability[p]) * random.randint(80,105) * c) / 100)+1
        ET[p, c, i] = ((taskComputationRequirement[i] / computationCapability[p]) * random.randint(80,105) * c) / 100

    for s,c,i in itertools.product(S,K,V):
        if s == 0:
            ET[s, c, i] = (taskComputationRequirement[i])
        if s == 1:
            ET[s, c, i] = ((taskComputationRequirement[i] / 20) * random.randint(80,105) * c) / 100
        if s == 2:
            ET[s, c, i] = ((taskComputationRequirement[i] / 15) * random.randint(80,105) * c) / 100
    #Communication time
    communicationData = {}
    sendingRate = {}
    for (i,j) in E:
        communicationData[i,j] = random.randint(5,50)/100
    for p,q in itertools.product(P, P):
        if pFromS[p] == pFromS[q]:
            sendingRate[p, q] = 0.6
            continue
        #car to edge communication
        if (pFromS[p] == numberOfCars and pFromS[q] < numberOfCars) or (pFromS[q] == numberOfCars and pFromS[p] < numberOfCars):
            sendingRate[p, q] = 1.25
        #car to cloud communication
        if (pFromS[p] == numberOfCars + 1 and pFromS[q] < numberOfCars) or (pFromS[q] == numberOfCars + 1 and pFromS[p] < numberOfCars):
            sendingRate[p, q] = 2
            # edge to cloud communication
        if (pFromS[p] == numberOfCars + 1 and pFromS[q] == numberOfCars) or (pFromS[q] == numberOfCars + 1 and pFromS[p] == numberOfCars):
            sendingRate[p, q] = 1.4
    CT = {}
    print("here")
    for p,q,c,c_,i,j in  itertools.product(P,P,C,C,V,V):
        break
        print(p,q,c,c_,i,j)
        if (i,j) not in E:
            continue
        if p == q:
            CT[p, q, c, c_, i, j] = 0
            continue
        if pFromS[p] < numberOfCars and pFromS[q] < numberOfCars:
            continue
        CT[p,q,c,c_,i,j] = (communicationData[i,j]/sendingRate[p,q])*c*0.9
    Trelease = []
    Tdue = []
    for c in C:
        Trelease.append([0 for i in range(25)])
        Tdue.append([i*8 +8for i in range(25)])

i = 0
j = 0

print("K:",K,"S:",S,"C:",C)
print(Ps)
print(pFromS)
print("P:", P)
print("V:", V)
print("VT:", VT)
print("E:", E)
for i in Isuc:
    print(i)
for i in range(7,3):
    print(i)
print("Ipr", Ipr)
print("Pc",Pc)
print("Trelease:",Trelease)
print("Tdue:", Tdue)
print(ET)
print(min(ET))
for i in V:
    for s in S:
        print("task",i,"on",s,"takes",ET[s,1,i])
# for p,c,i in itertools.product(P, K, V):
#     print("p:", p,"c:",c,"i:",i, "Time:",ET[p,c,i] , "p time:", computationCapability[p],"i time:",taskComputationRequirement[i])
# for (i,j) in E:
#     print(communicationData[i,j])
# for p,q in itertools.product(P,P):
#     if pFromS[p] < numberOfCars and pFromS[q] < numberOfCars:
#         continue
#     print("1st:",pFromS[p], "2nd:",pFromS[q],"rate:",sendingRate[p,q])
# quit()
# goToNextLine = input("Press return to go to resume")

#=========================ILP Model==========================
# ILP Model
aut = gp.Model('autonomous driving')
x = aut.addVars(S, V, C, vtype=GRB.BINARY,name='assignment')  # x[p][i][c] task i from car c assigned to processing unit p
y = aut.addVars(V, C, C, vtype=GRB.BINARY, name='aggregation')  # y[i][c][c'] task is aggregated from car c and c'
# t = aut.addVars(V, C, vtype=GRB.CONTINUOUS,lb=0,ub=30, name='starting time')  # t[i][c] starting time of task i from car c
t = aut.addVars(V, C, vtype=GRB.CONTINUOUS, name='starting time')  # t[i][c] starting time of task i from car c
# finTime = aut.addVars(V, C, P, vtype=GRB.INTEGER, name='starting time')  # t[i][c] starting time of task i from car c
# thetb = aut.addVars(V,V, C, C, vtype=GRB.BINARY, name='starting time')  # t[i][c] starting time of task i from car c
m = aut.addVars(V, C, vtype=GRB.INTEGER, name='number of cooperative cars')  # m[i][c] number of cooperative cars with car c in task i
# thet = aut.addVars(V, V, C, C, vtype=GRB.BINARY, name='task order')  # thet[i][j][c][c'] task i from car c have to finish before task j from car c' on \
# coAssign = aut.addVars(V, V, C, C, P, vtype=GRB.BINARY, name='Binary multiply value of x_{i,c,p} and x_{j,c_,p}')
# the same processing unit
# ret = aut.addVars(V, C, P, vtype=GRB.CONTINUOUS,lb=0,ub=20, name='execution time')  # ret[i,c,p] real execution time of task i from car c
ret = aut.addVars(V, C, S, vtype=GRB.CONTINUOUS, name='execution time')  # ret[i,c,p] real execution time of task i from car c
# ret = aut.addVars(V, C, P, vtype=GRB.CONTINUOUS,lb=0,ub=20, name='execution time')  # ret[i,c,p] real execution time of task i from car c
# ret = aut.addVars(V, C, P, vtype=GRB.INTEGER, name='execution time')  # ret[i,c,p] real execution time of task i from car c
# on processing unit p
# rct = aut.addVars(V, V, C, C, P, P, vtype=GRB.CONTINUOUS,lb=0,ub=5, name='communication time')  # rct[i,j,c,c',p,q] real communication time of task i and j
# from car c  and task i is aggregated from c'
# on processing unit p and q
L = aut.addVar(vtype=GRB.CONTINUOUS, name="objective")  # the last task finishing time

abCompKM = aut.addVars(V, C, K, vtype=GRB.INTEGER, name='absoloute value of k - M_{i,c}')  # abCompKM[i,c,k]
abCompKMb = aut.addVars(V, C, K, vtype=GRB.BINARY, name='Binary value of k - M_{i,c}')  # abCompKM[i,c,k]
# abCompStartingCoop = aut.addVars(V, C, C, vtype=GRB.CONTINUOUS,lb=0,ub=30, name='absoloute value of t_{i,c} and t_{i,c_}')  # abCompStartingCoop[i,c,c']
abCompStartingCoop = aut.addVars(V, C, C, vtype=GRB.CONTINUOUS, name='absoloute value of t_{i,c} and t_{i,c_}')  # abCompStartingCoop[i,c,c']
abCompStartingCoopb = aut.addVars(V, C, C, vtype=GRB.BINARY,name='Binary value of t_{i,c} and t_{i,c_}')  # abCompStartingCoop[i,c,c']
# abCompAssignCoop = aut.addVars(V, C, C, P, vtype=GRB.INTEGER,
#                                name='absoloute value of x_{i,c,p} and x_{i,c_,p}')  # abCompStartingCoop[i,c,c']
# abCompAssignCoopb = aut.addVars(V, C, C, P, vtype=GRB.BINARY,
#                                 name='Binary value of x_{i,c,p} and x_{i,c_,p}')  # abCompStartingCoop[i,c,c']
assignedServer = aut.addVars(V, C, vtype=GRB.INTEGER, name='the server that the task is assigned')
# communicationDelay = aut.addVars(V, V, C, vtype=GRB.INTEGER, name='the server that the task is assigned')
# multiXTime = aut.addVars(V,C,P,vtype=GRB.INTEGER,name='absoloute value of x_{i,c} and x_{i,c_}') #multiXTime[i,c,p]
# difAssign = aut.addVars(V, V, C, P, P, vtype=GRB.BINARY, name='Binary multiply value of x_{i,c,p} and x_{j,c_,p}')
#numAssign = aut.addVars(P, vtype=GRB.BINARY)
# we have 50 task
# 5 cars 50 * 50 * 5 = 7500
# ==================================================OBJECTIVE==================================

aut.setObjective(L, GRB.MINIMIZE)
print("num of cars:",numberOfCars,"num of tasks:",len(V),"num of processing units",len(P))
# ===================================================CONSTRAINTS==========================================

# for p in P:
#     aut.addConstr(sum(x[p, i, c] for i, c in itertools.product(V, C)) >= numAssign[p])  # (1)
# for p in P:
#     aut.addConstr(sum(x[p, i, c] for i, c in itertools.product(V, C)) <= numAssign[p] * 1000)  # (1)


# for i, c in itertools.product(V, C):
#     aut.addConstr(sum(x[p, i, c] for p in Pc[c]) == 1, "taskAssignment[%s,%s]" % (i, c))  # (1)


for i, c in itertools.product(V, C):
    aut.addConstr(sum(x[s, i, c] for s in S) == 1, "taskAssignment2[%s,%s]" % (i, c))  # mimic Constraint (2)

for i, c, c_ in itertools.product(V, C, C):
    if c != c_:
        aut.addConstr(x[0, i, c] + y[i,c,c_] <= 1, "taskAssignment2[%s,%s]" % (i, c))  # mimic Constraint (2)

# for i,j, c in itertools.product(V,V, C):
#     if (i,j) in E:
#         for k,p in itertools.product(K,P):
#             aut.addConstr(communicationDelay[i,j,c] <= abCompKM[i,c,k] * 1000 + CT[], "taskAssignment2[%s,%s]" % (i, c))  # mimic Constraint (2)
#     else:
#         aut.addConstr(communicationDelay[i,j,c] == 0, "taskAssignment2[%s,%s]" % (i, c))  # mimic Constraint (2)


for i, c, c_ in itertools.product(V, C, C):
    aut.addConstr(t[i, c] >= y[i, c, c_] * Trelease[c_][i], "startBeforeRelease[%s,%s,%s]" % (i, c, c_))  # (3)


# Linearization of startingTime + executionTime <= deadline =====================================
# (5)
# BEGIN Execution time
for i, c in itertools.product(V, C):
    aut.addConstr(sum(y[i, c, c_] for c_ in C) == m[i, c], "numOfCooperativeCars[%s,%s]" % (i, c))  # (5.1)


for i, c, s in itertools.product(V, C, S):
    aut.addConstr(ret[i, c, s] <= x[s, i, c] * 1000, "realExTimeZero[%s,%s,%s]" % (i, c, s))  # (5.2)


# |k - m_{i,c}| = abCompKM_{i,c,k} absoloute value of k - M_{i,c}
# Not in the paper
# BEGIN
# abCompKM_{i,c,k} >= |k - m_{i,c}|
for i, c, k in itertools.product(V, C, K):
    aut.addConstr(abCompKM[i, c, k] >= k - m[i, c], "Y >= X [%s,%s,%s]" % (i, c, k))
for i, c, k in itertools.product(V, C, K):
    aut.addConstr(abCompKM[i, c, k] >= m[i, c] - k, "Y >= -X [%s,%s,%s]" % (i, c, k))
# abCompKM_{i,c,k} <= |k - m_{i,c}|
for i, c, k in itertools.product(V, C, K):
    aut.addConstr(abCompKM[i, c, k] <= k - m[i, c] + 1000 * abCompKMb[i, c, k], "Y >= X [%s,%s,%s]" % (i, c, k))
for i, c, k in itertools.product(V, C, K):
    aut.addConstr(abCompKM[i, c, k] <= m[i, c] - k + 1000 * (1 - abCompKMb[i, c, k]), "Y >= -X [%s,%s,%s]" % (i, c, k))
# END

for i, c, k, s in itertools.product(V, C, K, S):
    aut.addConstr(ret[i, c, s] <= (ET[s, k, i] * x[s, i, c]) + (abCompKM[i, c, k] * 1000), "realExTimeZero[%s,%s,%s]" % (i, c, s))  # (5.3)

for i, c, k, s in itertools.product(V, C, K, S):
    aut.addConstr(ret[i, c, s] >= (ET[s, k, i] * x[s, i, c]) - (abCompKM[i, c, k] * 1000), "realExTimeZero[%s,%s,%s]" % (i, c, s))  # (5.4)


for i, c in itertools.product(V, C):
    aut.addConstr(t[i, c] + sum(ret[i, c, s] for s in S) <= Tdue[c][i])  # (5)

# Communication delay constraints
# BEGIN communication
# coAssign = Xi * Xj on p and q
# for i, j, c, p, q in itertools.product(V, V, C, P, P):
#     aut.addConstr(difAssign[i, j, c, p, q] <= x[p, i, c])
#     aut.addConstr(difAssign[i, j, c, p, q] <= x[q, j, c])
#     aut.addConstr(difAssign[i, j, c, p, q] + 1 >= x[q, j, c] + x[p, i, c])
# for i, j, c, c_, p, q in itertools.product(V, V, C, C, P, P):
#     aut.addConstr(rct[i, j, c, c_, p, q] >= -(abCompKM[i, c, k] * 1000) - (1 - difAssign[i, j, c, p, q]) * 1000 + CT[p, q, c, c_, i, j])

for i, j, c in itertools.product(V, V, C):
    if (i, j) in E:
        aut.addConstr(t[i, c] + sum(ret[i, c, s] for s in S) <= t[j, c])

# END communication
# #Constraint (5)
# #BEGIN
# #multiXTime[i,c,p] = x[p,i,c] * ret[i,c,p]
# #BEGIN
# #multiXTime[i,c,p] <= x[p,i,c] * 1000
# for i,c,p in itertools.product(V,C,P):
#   aut.addConstr(multiXTime[i,c,p] <= x[p,i,c] * 1000,"multiXTime <= x * 1000 [%s,%s,%s]" % (i,c,p))
# #multiXTime[i,c,p] <= ret[i,c,p] + (1-x[p,i,c]) * 1000
# for i,c,p in itertools.product(V,C,P):
#   aut.addConstr(multiXTime[i,c,p] <= ret[i,c,p] + (1-x[p,i,c]) * 1000,"multiXTime <= x * 1000 [%s,%s,%s]" % (i,c,p))
# #multiXTime[i,c,p] >= ret[i,c,p] - (1-x[p,i,c]) * 1000
# for i,c,p in itertools.product(V,C,P):
#   aut.addConstr(multiXTime[i,c,p] >= ret[i,c,p] - (1-x[p,i,c]) * 1000,"multiXTime <= x * 1000 [%s,%s,%s]" % (i,c,p))
# #END
# for i,c in itertools.product(V,C):
#   aut.addConstr(t[i,c] + sum(multiXTime[i,c,p] for p in P) <= Trelease[c][i]) #(5)
# #END
# END Execution time

# for i,c in itertools.product(V,C):
#   aut.addConstr(t[i,c] + sum(multiXTime[i,c,p] for p in P) <= L) #(4)
for i, c in itertools.product(V, C):
    aut.addConstr(t[i, c] + sum(ret[i, c, s] for s in S) <= L)  # (4)

# *****
# # Theta constriants
# # BEGIN
# for i, c, c_ in itertools.product(V, C, C):
#     aut.addConstr(thet[i, i, c, c_] <= 1 - y[i, c, c_])  # (6)
#
# # coAssign = Xi * Xj on p
# for i, j, c, c_, p in itertools.product(V, V, C, C, P):
#     aut.addConstr(coAssign[i, j, c, c_, p] <= x[p, i, c])
# for i, j, c, c_, p in itertools.product(V, V, C, C, P):
#     aut.addConstr(coAssign[i, j, c, c_, p] <= x[p, j, c_])
# for i, j, c, c_, p in itertools.product(V, V, C, C, P):
#     aut.addConstr(coAssign[i, j, c, c_, p] + 1 >= x[p, i, c] + x[p, j, c_])
# # theta <= coAssign
# for i, j, c, c_ in itertools.product(V, V, C, C):
#     aut.addConstr(thet[i, j, c, c_] <= sum(coAssign[i, j, c, c_, p] for p in P))
# # thetai,j + thetaj,i <= 1
# for i, j, c, c_ in itertools.product(V, V, C, C):
#     aut.addConstr(thet[i, j, c, c_] + thet[j, i, c_, c] <= 1)
# # if coAssign = 1 and i=j and Y = 0 then theta = 1
# for i, c, c_ in itertools.product(V, C, C):
#     aut.addConstr(thet[i, i, c, c_] + thet[i, i, c_, c] - sum(coAssign[i, i, c, c_, p] for p in P) + y[i, c, c_] >= 0)
# # if coAssign = 1 and i!=j then theta = 1
# for i, j, c, c_ in itertools.product(V, V, C, C):
#     if i != j:
#         aut.addConstr(thet[i, j, c, c_] + thet[j, i, c_, c] - sum(coAssign[i, j, c, c_, p] for p in P) >= 0)
# # THETA CONSTRAINT
# for i, j, c, c_ in itertools.product(V, V, C, C):
#     aut.addConstr(t[i, c] + sum(ret[i, c, p] for p in P) + (thet[i, j, c, c_] - 1) * 1000 <= t[j, c_])
# # END
# ****
# #two different tasks(they are not cooperating) assigned to the same processing unit can not be run simultaneously
# for i,j,c,c_,p in itertools.product(V,V,C,C,P):
#     if i!=j:
#         aut.addConstr(t[i,c] + ret[i,c,p] - infNum*thetb[i,j,c,c_] <= t[j,c_])
#         aut.addConstr(t[i,c] + infNum*(1-thetb[i,j,c,c_]) >= t[j,c] + ret[j,c_,p] - infNum*(1-x[p,i,c]))
#     if i == j:
#         aut.addConstr(t[i, c] + ret[i, c, p] - infNum * thetb[i,j,c,c_] - infNum * y[i,c,c_] <= t[j, c_])
#         aut.addConstr(t[i, c] + infNum * (1 - thetb[i,j,c,c_]) >= t[j, c] + ret[j, c_, p] - infNum * (1 - x[p, i, c]) - infNum * y[i,c,c_])
# Linearization of (10)
# BEGIN
# abCompAssignCoop[i,c,c',p] = |x[p,i,c] - x[p,i,c']|
# BEGIN
# abCompAssignCoop[i,c,c',p] >= |x[p,i,c] - x[p,i,c']|
# for i, c, c_, p in itertools.product(V, C, C, P):
#     aut.addConstr(abCompAssignCoop[i, c, c_, p] >= x[p, i, c] - x[p, i, c_])
# for i, c, c_, p in itertools.product(V, C, C, P):
#     aut.addConstr(abCompAssignCoop[i, c, c_, p] >= x[p, i, c_] - x[p, i, c])
# # abCompAssignCoop[i,c,c',p] <= |x[p,i,c] - x[p,i,c']|
# for i, c, c_, p in itertools.product(V, C, C, P):
#     aut.addConstr(abCompAssignCoop[i, c, c_, p] <= x[p, i, c] - x[p, i, c_] + 1000 * abCompAssignCoopb[i, c, c_, p])
# for i, c, c_, p in itertools.product(V, C, C, P):
#     aut.addConstr(abCompAssignCoop[i, c, c_, p] <= x[p, i, c_] - x[p, i, c] + 1000 * (1 - abCompAssignCoopb[i, c, c_, p]))
# # END
# for i, c, c_, p in itertools.product(V, C, C, P):
#     aut.addConstr(abCompAssignCoop[i, c, c_, p] <= 1000 * (1 - y[i, c, c_]))
#task i of c assigned to which server
for i,c in itertools.product(V,C):
    assignedServer[i,c] = sum((x[p,i,c] * s) for s in S)
#if y =1 then Xi,c == Xi,c_
for i,c,c_ in itertools.product(V,C,C):
    (1-y[i,c,c_])*1000 + (assignedServer[i,c] - assignedServer[i,c_]) >= 0
    (y[i,c,c_]-1)*1000 + (assignedServer[i,c] - assignedServer[i,c_]) >= 0
    ######In moshkel dare
# END

# Linearization of (11)
# BEGIN
# abCompStartingCoop[i,c,c'] = |t[i,c] - t[i,c']|
# BEGIN
# abCompStartingCoop[i,c,c'] >= |t[i,c] - t[i,c']|
for i, c, c_ in itertools.product(V, C, C):
    aut.addConstr(abCompStartingCoop[i, c, c_] >= t[i, c] - t[i, c_], "Y >= X [%s,%s,%s]" % (i, c, c_))
for i, c, c_ in itertools.product(V, C, C):
    aut.addConstr(abCompStartingCoop[i, c, c_] >= t[i, c_] - t[i, c], "Y >= -X [%s,%s,%s]" % (i, c, c_))
# abCompStartingCoop[i,c,c'] <= |t[i,c] - t[i,c']|
for i, c, c_ in itertools.product(V, C, C):
    aut.addConstr(abCompStartingCoop[i, c, c_] <= t[i, c] - t[i, c_] + 1000 * abCompStartingCoopb[i, c, c_], "Y >= X [%s,%s,%s]" % (i, c, c_))
for i, c, c_ in itertools.product(V, C, C):
    aut.addConstr(abCompStartingCoop[i, c, c_] <= t[i, c_] - t[i, c] + 1000 * (1 - abCompStartingCoopb[i, c, c_]), "Y >= -X [%s,%s,%s]" % (i, c, c_))
# END
for i, c, c_ in itertools.product(V, C, C):
    aut.addConstr(abCompStartingCoop[i, c, c_] <= 1000 * (1 - y[i, c, c_]), "Y >= -X [%s,%s,%s]" % (i, c, c_))
# END

for i, j, c, c_ in itertools.product(V, V, C, C):
    if j in Isuc[i]:
        aut.addConstr(y[i, c, c_] <= y[j, c, c_], "realExTimeZero[%s,%s]" % (i, c))  # (12)


for i, c in itertools.product(V, C):
    aut.addConstr(y[i, c, c] == 1, "har kas dare ba khodesh hamkarii mikone")  # (13)


for i, c, c_ in itertools.product(V, C, C):
    if VT[i] == 1:
        continue
    aut.addConstr(y[i, c, c_] == y[Ipr[i], c, c_], "")  # (14) If they got aggregated at the previous aggregable node so they have to get aggregated at the current node


aut.optimize()
print("PAUSE THE PROGEAM")
# print("========m[i,c]========")
# for i in V:
#   for c in C:
#     for k in K:
#       print("i:",i,"c:",c,"k:",k,"",abCompKM[i,c,k].X)
try:
    print("Finishing time of ILP:",L.X)
    print("===============Assignment=========")
    for c, i, s in itertools.product(C, V, S):
        if x[s, i, c].X == 1:
            print("task ", i, " of ", c, " ==> ", s, " at ", t[i, c].X, " taskes ", ret[i, c, s].X)
    # print("==================theta=================")
    # print("i    j    c    c\'")
    # for i, j, c, c_ in itertools.product(V, V, C, C):
    #     if (thet[i, j, c, c_].X == 1):
    #         print(i, "  ", j, "  ", c, "  ", c_)
    print("===============Collaboration=========")
    for i, c, c_ in itertools.product(V, C, C):
        if c == c_:
            continue
        if y[i, c, c_].X == 1:
            print("task ", i, " of ", c, " and ", c_)
    print("===============Collaboration=========")
    for i in V:
        checked = []
        result = ""
        for c in C:
            if c in checked:
                continue
            checked.append(c)
            cooperators = []
            for c_ in C:
                if y[i, c, c_].X == 1:
                    cooperators.append(c_)
                    checked.append(c_)
            if len(cooperators) > 0:
                result += str(cooperators)
        print("task ", i, " Coop:", result)
    print("===============Objective=========")
    print("the last task finished at ", L.X)
    # print("testing abcompKM")
    # for i,c,k in itertools.product(V,C,K):
    #     print("i:",i,"c:",c,"k:",k,"m[i,c] - k:",m[i,c].X - k, "abcomp",abCompKM[i,c,k].X)
except:
    print("ILP sucks")

# =========================END of ILP Model====================

queue = []
schedulledTasks = {}  # schedulledTasks[i,c] task i of car c
schedulledTasksList = []
startingTime = {}
releaseTime = {}
clock = 0
# add the root taks to queue
for c in C:
    temp = task(0,[c])
    queue.append(temp)
    releaseTime[temp] = 0
path = {}  # path[i]

for i in V:
    result = []
    for j in V:
        if (i, j) in E:
            result.append([j])
    while True:
        tempResult = []
        if len(result) == 0:  # last node in the path
            break
        for pat in result:
            if pat == None:
                continue
            lastEl = pat[len(pat) - 1]
            tempCounter = 0
            for j in V:
                if (lastEl, j) in E:
                    tempCounter = 1
                    tempResult.append(pat + [j])
            if tempCounter == 0:
                tempResult.append(pat)
        if tempResult == result:
            break
        result = tempResult
    path[i] = result

idleTime = {}  # idleTime[p] when p is available
for p in P:
    idleTime[p] = 0

# parent nodes determine which node have to be executed before the task
parentNodes = {}
for i in V:
    result = []
    for j in V:
        if (j, i) in E:
            result.append(j)
    parentNodes[i] = result

# Greedy Scheduling
criticalTime = {}  # criticalTiem[i] how long does critical path of i take to execute
bestProc = {}  # what is the best platform for task (i,c) and even aggregated tasks
execTime = {}
execTimeOnP = {}  # exec time of task i from queue on p

criticalTimeAgg = {}  # criticalTiem[i] how long does critical path of i take to execute
bestProcAgg = {}  # what is the best processor for task (i,c) and even aggregated tasks
execTimeAgg = {}
execTimeOnPAgg = {}  # exec time of task i from queue on p
print("GREEDY STATRS")
#=========New Greedy===============
while len(queue) > 0:
    increaseClockByOne = 1
    minReleaseTime = infNum
    #update the greedy value of each individual task
    for i in queue:#idivdual tasks
        if releaseTime[i] > clock:
            if minReleaseTime > releaseTime[i]:
                minReleaseTime = releaseTime[i]
            continue
        increaseClockByOne = 0
        bestProc[i] = 0
        numOfCar = len(i.cars)
        execTime[i] = infNum
        for p in S:
            #if the processor is busy so the time is infinity
            # if clock < idleTime[p]:
            #     execTimeOnP[p,i] = infNum
            #     continue

            tempExecTime = ET[p,numOfCar, i.ID]
            criticalPathTime = 0

            # find the critical path
            for pat in path[i.ID]:
                tempCriticalTime = 0
                for tas in pat:
                    tempCriticalTime += ET[p,numOfCar,i.ID]
                if tempCriticalTime > criticalPathTime:
                    criticalPathTime = tempCriticalTime
            execTimeOnP[p,i] = tempExecTime + criticalPathTime

            # update the best proccessor
            if execTimeOnP[p,i] <= execTime[i]:
                execTime[i] = execTimeOnP[p,i]
                bestProc[i] = p

    feasibleAggregation = []
    ##update the greedy value of each aggregation
    for i,j in itertools.product(queue,queue):
        if releaseTime[i] > clock or releaseTime[j] > clock:
            continue
        if i.ID != j.ID:
            continue
        if VT[i.ID] == 0:
            continue
        if i == j:
            continue
        if (j,i) in feasibleAggregation:
            continue
        feasibleAggregation.append((i,j))
        numOfCar = len(i.cars) + len(j.cars)
        bestProcAgg[(i,j)] = 0
        execTimeAgg[(i,j)] = infNum
        for p in S:
            # if the processor is busy so the time is infinity
            # if clock < idleTime[p]:
            #     execTimeOnPAgg[p, (i,j)] = infNum
            #     continue

            tempExecTime = ET[p, numOfCar, i.ID]
            criticalPathTime = 0

            # find the critical path
            for pat in path[i.ID]:
                tempCriticalTime = 0
                for tas in pat:
                    tempCriticalTime += ET[p, numOfCar, i.ID]
                if tempCriticalTime > criticalPathTime:
                    criticalPathTime = tempCriticalTime
            execTimeOnPAgg[p, (i,j)] = tempExecTime + criticalPathTime

            # update the best proccessor
            if execTimeOnPAgg[p, (i,j)] <= execTimeAgg[(i,j)]:
                execTimeAgg[(i,j)] = execTimeOnPAgg[p, (i,j)]
                bestProcAgg[(i,j)] = p

    #finding the best individual task
    suitableTask = queue[0]
    suitableTaskGreedyValue = infNum
    for i in queue:
        if releaseTime[i] > clock:
            continue
        TdueOfi = infNum
        for car in i.cars:
            if Tdue[car][i.ID] <= TdueOfi:
                TdueOfi = Tdue[car][i.ID]
        greedyValueOfi = TdueOfi - execTime[i]
        if suitableTaskGreedyValue > greedyValueOfi:
            suitableTaskGreedyValue = greedyValueOfi
            suitableTask = i



    #finding the best aggregation
    aggregationb = 0
    if len(feasibleAggregation) > 0:
        suitableTaskAgg = feasibleAggregation[0]
    suitableTaskGreedyValueAgg = infNum
    for tas in feasibleAggregation:
        tasi = tas[0]
        tasj = tas[1]
        TdueOfi = infNum
        for car in tasi.cars:
            if Tdue[car][tasi.ID] < TdueOfi:
                TdueOfi = Tdue[car][tasi.ID]
        TdueOfj = infNum
        for car in tasj.cars:
            if Tdue[car][tasj.ID] < TdueOfj:
                TdueOfj = Tdue[car][tasj.ID]
        greedyValueOfij = min(TdueOfi,TdueOfj) - min(execTime[tasi],execTime[tasj]) + (execTimeAgg[tas] - execTime[tasi]/2 - execTime[tasj]/2)
        if greedyValueOfij < suitableTaskGreedyValueAgg:
            suitableTaskGreedyValueAgg = greedyValueOfij
            suitableTaskAgg = tas

    if suitableTaskGreedyValueAgg < suitableTaskGreedyValue:
        taski = suitableTaskAgg[0]
        taskj = suitableTaskAgg[1]
        queue.remove(taski)
        queue.remove(taskj)
        temp = task(taski.ID,taski.cars+taskj.cars)
        schedulledTasks[temp] = bestProcAgg[suitableTaskAgg]
        schedulledTasksList.append(temp)
        p = bestProcAgg[suitableTaskAgg]
        bestProcAgg[temp] = p
        # startingTime[temp] = idleTime[p]
        startingTime[temp] = clock
        # idleTime[p] += execTimeOnPAgg[p,suitableTaskAgg] wrong line
        # idleTime[p] += ET[p,len(taski.cars+taskj.cars),taski.ID]
        for edge in E:
            if edge[0] == taski.ID:
                temp = task(edge[1], taski.cars+taskj.cars)
                queue.append(temp)
                # releaseTime[temp] = idleTime[p]
                releaseTime[temp] = clock + ET[p,len(taski.cars+taskj.cars),taski.ID]
    else:
        if increaseClockByOne == 1:
            clock = minReleaseTime
            continue
        queue.remove(suitableTask)
        idd = suitableTask.ID
        numOfCar = len(suitableTask.cars)
        schedulledTasksList.append(suitableTask)
        schedulledTasks[suitableTask] = bestProc[suitableTask]
        p = bestProc[suitableTask]
        # startingTime[suitableTask] = idleTime[p]
        startingTime[suitableTask] = clock
        # idleTime[p] += execTimeOnP[p,suitableTask] wrong line
        # idleTime[p] += ET[p,numOfCar,idd]
        for edge in E:
            if edge[0] == idd:
                goToQueue = 1
                tempTask = task(edge[1], suitableTask.cars)
                if tempTask in releaseTime:
                    if releaseTime[tempTask] < clock + ET[p,numOfCar,idd]:
                        releaseTime[tempTask] = clock + ET[p,numOfCar,idd]
                else:
                    releaseTime[tempTask] = clock + ET[p,numOfCar,idd]
                for tas in parentNodes[edge[1]]:
                    temp = task(idd,suitableTask.cars)
                    if temp not in schedulledTasksList:
                        goToQueue = 0
                        break
                if goToQueue == 1:
                    queue.append(tempTask)
                    # releaseTime[tempTask] = idleTime[p]

    if increaseClockByOne == 1:
        clock = minReleaseTime
        continue


    #!@#$
    #update release time and clock
    #update Idle time
    #then update queue

    #update clock
    # clock = idleTime[0]
    # for p in P:
    #     if idleTime[p] < clock:
    #         clock = idleTime[p]
    # print(path)
print("ID  cars  start server")
for i in schedulledTasksList:
    checked = []
    result = ""
    cooperators = []
    for c in C:
        if c in checked:
            continue
        checked.append(c)
        for c_ in C:
            if y[i.ID, c, c_].X == 1:
                cooperators.append(c_)
                checked.append(c_)
        if len(cooperators) > 0:
            result += str(cooperators)
    for s in S:
        if x[s,i.ID,cooperators[0]].X == 1:
            print("ILP:    task ", i.ID, " Cars:", result, " ==> ", s, " start at ", t[i.ID, c].X, " taskes ", ret[i.ID, c, s].X)
    if i in bestProc:
        print("Greedy:",i,"starts at",startingTime[i]," on", bestProc[i],"takes",ET[bestProc[i],len(i.cars),i.ID],"finishes at",startingTime[i]+ET[bestProc[i],len(i.cars),i.ID])
        # print(i.ID, " ", i.cars," ", startingTime[i]," ", bestProc[i])
    else:
        print("Greedy",i,"starts at",startingTime[i]," on", bestProcAgg[i],"takes",ET[bestProc[i],len(i.cars),i.ID],"finishes at",startingTime[i]+ET[bestProc[i],len(i.cars),i.ID])
        # print(i.ID, " ", i.cars, " ", startingTime[i], " ", bestProcAgg[i])
print("Finishing time of ILP:",L.X)


# clock = idleTime[0]
# for p in P:
#     if idleTime[p] > clock:
#         clock = idleTime[p]
# print("Finishing time of Greedy:", clock)
#=========END of New Greedy============
quit()
while len(queue) > 0:
    increaseClockByOne = 1
    minReleaseTime = infNum
    for i in queue:#idivdual tasks
        if releaseTime[i] > clock:
            if minReleaseTime > releaseTime[i]:
                minReleaseTime = releaseTime[i]
            continue
        increaseClockByOne = 0
        bestProc[i] = 0
        numOfCar = len(i.cars)
        execTime[i] = infNum
        for p in S:
            #if the processor is busy so the time is infinity
            if clock < idleTime[p]:
                execTimeOnP[p,i] = infNum
                continue

            tempExecTime = ET[p,numOfCar, i.ID]
            criticalPathTime = 0

            # find the critical path
            for pat in path[i.ID]:
                tempCriticalTime = 0
                for tas in pat:
                    tempCriticalTime += ET[p,numOfCar,i.ID]
                if tempCriticalTime > criticalPathTime:
                    criticalPathTime = tempCriticalTime
            execTimeOnP[p,i] = tempExecTime + criticalPathTime

            # update the best proccessor
            if execTimeOnP[p,i] <= execTime[i]:
                execTime[i] = execTimeOnP[p,i]
                bestProc[i] = p

    feasibleAggregation = []
    # aggregate two task
    for i,j in itertools.product(queue,queue):
        if releaseTime[i] > clock or releaseTime[j] > clock:
            continue
        if i.ID != j.ID:
            continue
        if VT[i.ID] == 0:
            continue
        if i == j:
            continue
        if (j,i) in feasibleAggregation:
            continue
        feasibleAggregation.append((i,j))
        numOfCar = len(i.cars) + len(j.cars)
        bestProcAgg[(i,j)] = 0
        execTimeAgg[(i,j)] = infNum
        for p in P:
            # if the processor is busy so the time is infinity
            if clock < idleTime[p]:
                execTimeOnPAgg[p, (i,j)] = infNum
                continue

            tempExecTime = ET[p, numOfCar, i.ID]
            criticalPathTime = 0

            # find the critical path
            for pat in path[i.ID]:
                tempCriticalTime = 0
                for tas in pat:
                    tempCriticalTime += ET[p, numOfCar, i.ID]
                if tempCriticalTime > criticalPathTime:
                    criticalPathTime = tempCriticalTime
            execTimeOnPAgg[p, (i,j)] = tempExecTime + criticalPathTime

            # update the best proccessor
            if execTimeOnPAgg[p, (i,j)] <= execTimeAgg[(i,j)]:
                execTimeAgg[(i,j)] = execTimeOnPAgg[p, (i,j)]
                bestProcAgg[(i,j)] = p

    #finding the next to get schedulled
    suitableTask = queue[0]
    suitableTaskGreedyValue = infNum
    for i in queue:
        if releaseTime[i] > clock:
            continue
        TdueOfi = infNum
        for car in i.cars:
            if Tdue[car][i.ID] <= TdueOfi:
                TdueOfi = Tdue[car][i.ID]
        greedyValueOfi = TdueOfi - execTime[i]
        if suitableTaskGreedyValue > greedyValueOfi:
            suitableTaskGreedyValue = greedyValueOfi
            suitableTask = i

    if increaseClockByOne == 1:
        clock = minReleaseTime
        continue
    aggregationb = 0
    if len(feasibleAggregation) > 0:
        suitableTaskAgg = feasibleAggregation[0]
    suitableTaskGreedyValueAgg = infNum
    for tas in feasibleAggregation:
        tasi = tas[0]
        tasj = tas[1]
        TdueOfi = infNum
        for car in tasi.cars:
            if Tdue[car][tasi.ID] < TdueOfi:
                TdueOfi = Tdue[car][tasi.ID]
        TdueOfj = infNum
        for car in tasj.cars:
            if Tdue[car][tasj.ID] < TdueOfj:
                TdueOfj = Tdue[car][tasj.ID]
        greedyValueOfij = min(TdueOfi,TdueOfj) - min(execTime[tasi],execTime[tasj]) + (execTimeAgg[tas] - execTime[tasi]/2 - execTime[tasj]/2)
        if greedyValueOfij < suitableTaskGreedyValueAgg:
            suitableTaskGreedyValueAgg = greedyValueOfij
            suitableTaskAgg = tas

    if suitableTaskGreedyValueAgg < suitableTaskGreedyValue:
        taski = suitableTaskAgg[0]
        taskj = suitableTaskAgg[1]
        queue.remove(taski)
        queue.remove(taskj)
        temp = task(taski.ID,taski.cars+taskj.cars)
        schedulledTasks[temp] = bestProcAgg[suitableTaskAgg]
        schedulledTasksList.append(temp)
        p = bestProcAgg[suitableTaskAgg]
        bestProcAgg[temp] = p
        startingTime[temp] = idleTime[p]
        # idleTime[p] += execTimeOnPAgg[p,suitableTaskAgg] wrong line
        idleTime[p] += ET[p,len(taski.cars+taskj.cars),taski.ID]
        for edge in E:
            if edge[0] == taski.ID:
                temp = task(edge[1], taski.cars+taskj.cars)
                queue.append(temp)
                releaseTime[temp] = idleTime[p]
    else:
        queue.remove(suitableTask)
        idd = suitableTask.ID
        numOfCar = len(suitableTask.cars)
        schedulledTasksList.append(suitableTask)
        schedulledTasks[suitableTask] = bestProc[suitableTask]
        p = bestProc[suitableTask]
        startingTime[suitableTask] = idleTime[p]
        # idleTime[p] += execTimeOnP[p,suitableTask] wrong line
        idleTime[p] += ET[p,numOfCar,idd]
        for edge in E:
            if edge[0] == idd:
                goToQueue = 1
                tempTask = task(edge[1], suitableTask.cars)
                for tas in parentNodes[edge[1]]:
                    temp = task(idd,suitableTask.cars)
                    if temp not in schedulledTasksList:
                        goToQueue = 0
                        break
                if goToQueue == 1:
                    queue.append(tempTask)
                    releaseTime[tempTask] = idleTime[p]




    #!@#$
    #update release time and clock
    #update Idle time
    #then update queue

    #update clock
    clock = idleTime[0]
    for p in P:
        if idleTime[p] < clock:
            clock = idleTime[p]
    # print(path)
print("ID  cars  start server")
for i in schedulledTasksList:
    if i in bestProc:
        print(i,"starts at",startingTime[i]," on", bestProc[i])
        # print(i.ID, " ", i.cars," ", startingTime[i]," ", bestProc[i])
    else:
        print(i,"starts at",startingTime[i]," on", bestProcAgg[i])
        # print(i.ID, " ", i.cars, " ", startingTime[i], " ", bestProcAgg[i])

clock = idleTime[0]
for p in P:
    if idleTime[p] > clock:
        clock = idleTime[p]
print("Finishing time of Greedy:", clock)

#================Estimation===================
#numberOfCars
result = [i for i in range(numberOfCars)]
sum = [0 for i in range(numberOfCars)]
sum2 = [0 for i in range(numberOfCars)]
for i in result:
    bestIthProcCapability = sorted(computationCapability, reverse=True)[i]
    bestIthProcIndex = computationCapability.index(bestIthProcCapability)
    # print(computationCapability)
    # print("===")
    for j in V:
        sum[i] += ET[bestIthProcIndex,1,j]
        sum2[i] += ET[bestIthProcIndex,2,j]

print("Max:",max(sum+sum2))
print("Min:",min(sum+sum2))
print(sum,sum2)
