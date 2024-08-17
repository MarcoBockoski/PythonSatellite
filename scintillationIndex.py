# -*- coding: utf-8 -*-
"""
Created on Tue Jul 16 15:33:56 2024

@author: Marco Antonio
"""

import numpy as np

import math as m

def ScintillationIndex(r):
    I = r**2  # Intensity = amplitude^2
    s4 = np.std(I) / np.mean(I)
    
    temp = I / np.mean(I)
    minfad = 10 * np.log10(np.min(temp))
    tau0 = 1

    cov_ww = np.correlate(r - np.mean(r), r - np.mean(r), mode='full') / (np.std(r) * len(r))
    cov_ww = cov_ww[len(r)-1:]  # Keep only non-negative lags
    s = np.sign(cov_ww - np.exp(-1))  # Discriminating signal in +-1 with transition at point tau0

    i1 = np.where(s == -1)[0]
    print("s4:")
    print(s4)
    if s4 < 0.2:  # Assign tau0=NaN for S4<0.2
        tau0 = np.nan
    else:
        if len(i1) == 0:
            tau0 = np.nan
        else:
            tau0 = 0.02 * i1[0]  # Multiply by the sampling frequency to find tau0 in seconds

    return s4, minfad, tau0

def LeitorTXT(arquivo):
    matriz = []
    linesize = 0
    with open(arquivo, "r") as textFile:
        #info = []
        
        for line in textFile:
            linesize += 1
            
            #for item in line.split(','):
            #    info.append(item.strip())
                
            info = [item.strip() for item in line.split(',')]
            col7 = m.pow(int(info[4]),2) + m.pow(int(info[5]), 2)
            info.insert(6, col7)
            matriz.append(info)
            #if(linesize>99999): break;
            
    matriz = np.array([matriz], dtype='f8')
    matriz =  np.reshape(matriz, (linesize, 7))

    unq = np.unique(matriz[:, 1:3], axis = 0)

    temp = []

    for i in range(int(unq.size/2)):
        i = np.where((matriz[:, 1] == unq[i][0]) & (matriz[:, 2] == unq[i][1]))[0]
        temp.append(matriz[i, :])
    
    return temp, unq

temp, unq = LeitorTXT(f"../../Desktop/6col.txt")

# Assuming IQ_L1 is a 2D NumPy array with at least 6 columns
IQ_L1 = np.array(temp[0])  # Replace with actual data

# Calculate int_L1
int_L1 = IQ_L1[:, 4]**2 + IQ_L1[:, 5]**2

print("int_L1:")
print(int_L1)
print("\n")

# Determine LL
LL = int(np.floor(len(int_L1) / 3000))

print("LL:")
print(LL)
print("\n")

# Truncate int_L1 to LL * 3000 length
int_L1 = int_L1[:LL * 3000]

print("int_L1:")
print(int_L1)
print("\n")

# Reshape int_L1 to a 2D array with 3000 rows and LL columns
yy_L1 = int_L1.reshape((3000, LL))

print("yy_L1:")
print(yy_L1)
print("\n")

# Initialize results arrays
s4_L1 = np.zeros(LL)
minfad_L1 = np.zeros(LL)
tau0_L1 = np.zeros(LL)

# Calculate scintillation indices
for i in range(LL):
    s4_L1[i], minfad_L1[i], tau0_L1[i] = ScintillationIndex(np.sqrt(yy_L1[:, i]))

# Example output
print("LL:")
print(LL)
#print(f"s4_L1: {s4_L1}")
print(f"minfad_L1: {minfad_L1}")
#print(f"tau0_L1: {tau0_L1}")