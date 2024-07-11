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
with open("6col.txt", "r") as textFile:
    #info = []
    
    for line in textFile:
        linesize += 1
        
        #for item in line.split(','):
        #    info.append(item.strip())
            
        info = [item.strip() for item in line.split(',')]
        col7 = int(info[4]) + m.pow(int(info[5]), 2)
        info.insert(6, col7)
        matriz.append(info)
        #if(linesize>99999): break;
        
matriz = np.array([matriz], dtype='f8')
matriz =  np.reshape(matriz, (linesize, 7))
print("ori:")
print(matriz)
print("\n")

#unq, cts= np.unique(matriz[:, 1:3], return_counts = True, axis = 0)
#print("cts:")
#print(cts)
#print("\n")

unq = np.unique(matriz[:, 1:3], axis = 0)

print("size:")
print(unq.size/2)
print("\n")

print("unq:")
print(unq)
print("\n")

print(unq[0][0])
print(unq[1][0])

#i = np.where((matriz[:, 1] == 5) & (matriz[:, 2] == 0))[0]
#temp.append(matriz[i, :])

#np.savetxt("teste.txt", temp, header = "tempo | satelite | tipo sinal | fase | I | Q | I+Q²", fmt="%.3f")

temp = []

for i in range(int(unq.size/2)):
    i = np.where((matriz[:, 1] == unq[i][0]) & (matriz[:, 2] == unq[i][1]))[0]
    temp.append(matriz[i, :])
    
#print(len(temp[6]))
#np.savetxt("teste.txt", temp[6], header = "tempo | satelite | tipo sinal | fase | I | Q | I+Q²", fmt="%.3f")
    
for valor in range(len(temp)):
    np.savetxt(f"../../Desktop/safe/{unq[valor][0]}x{unq[valor][1]}.txt", temp[valor], header = "tempo | satelite | tipo sinal | fase | I | Q | I+Q²", fmt='%s')

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


