# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import numpy as np

import math as m

import matplotlib.pyplot as plt

def Media(matriz, init, fin):
    res = 0
    for index in range(init, fin):
        res = res + matriz[index][6]
    res = res/3000
    
    return res

def Desvio(matriz, media, index):
    res = matriz[index][6] - media
    return res

def Dp(matriz, init, fin):
    med = float(Media(matriz, init, fin))
    print(med)
    res = 0
    for index in range(init, fin):
        res = res + m.pow(Desvio(matriz, med, index), 2)
    res = res/3000
    res = m.sqrt(res)
    return res

matriz = []

#estrutura condicional/repetição "with": 
#strip == trimm do java (tira sufixos de espaços em branco)
#split == separa a linha em várias substrings separadas pelo caractere ","

print("  tempo | satelite | tipo sinal | fase | I | Q | I+Q²")

linesize = 0
with open("amostra.txt", "r") as textFile:
    #info = []
    
    for line in textFile:
        linesize += 1
        
        #for item in line.split(','):
        #    info.append(item.strip())
            
        info = [item.strip() for item in line.split(',')]
        col7 = int(info[4]) + m.pow(int(info[5]), 2)
        info.insert(6, col7)
        matriz.append(info)
        
matriz = np.array([matriz], dtype='f8')
matriz =  np.reshape(matriz, (linesize, 7))
print("ori:")
print(matriz)
print("\n")

#blabla
#blablabla

unq, num, inv, cts = np.unique(matriz[:, 1:3], return_index = True, return_inverse = True, return_counts = True, axis = 0)

print("size:")
print(unq.size/2)
print("\n")

print("unq:")
print(unq)
print("\n")

print("cts:")
print(cts)
print("\n")

print("num:")
print(num)
print("\n")

print("inv:")
print(inv)
print("\n")


#criar uma estrutura do loop que percorre a MATRIZ, criando submatrizes correspondentes aos filtros de unq

novo = np.repeat(unq, cts, axis = 0)

print(linesize)
print(num.size)
print(novo.size)
print(matriz.size)

for index in range(linesize):
    novo = np.insert(novo, (7*index)+2, matriz[num[inv[index]], [0,3,4,5,6]])

novo = np.reshape(novo, (linesize, 7))

print(novo)

np.savetxt("res.txt", novo, header = "satelite | tipo sinal | tempo | fase | I | Q | I+Q²" ,fmt="%.3f")


monobloconp = np.array([[a, str(b), c, d, e, f, g] for a,b,c,d,e,f,g in novo], dtype='O')
#monobloco = np.reshape(monobloco, (int(unq.size/2), cts[0], 7))



acc = 0
monobloco = []



print("fim")

for i in range(cts.size):
    monoaux = []
    for j in range(cts[i]): 
        monoaux.append(monobloconp[acc])
        acc += 1
    monobloco.append([monoaux])
print(acc)


for valor in range(len(monobloco)):
    np.savetxt(f"../../Desktop/safe/{monobloco[valor][0][0][0]}x{monobloco[valor][0][0][1]}.txt", monobloco[valor][0], header = "satelite | tipo sinal | tempo | fase | I | Q | I+Q²", fmt='%s')

print(monobloco[0])

print("fim")

"""dp = []
valores = []

for index in range(0, linesize, 3000):
   dp.append(Dp(matriz, index, index+3000))
   valores.append(index)

print(dp)

plt.plot(valores, dp)
plt.show()

print(valores)"""


