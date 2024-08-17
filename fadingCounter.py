import numpy as np

def fadingCounter(array3D, threshold):
    numfad = []
    for array2D in array3D:
        #coverte em dB, transforam 0dB em -30dB e cria o valor com threshold
        x = 10.0 * np.log10(np.where(array2D == 0, 10**(-30/10), array2D)) + threshold 
        
        #se o valor se apresenta abaixo do limite (valor em dB > threshold), cria um vetor booleano
        below_threshold = x < 0
        
        #se não tem ninguém abaixo do limite, Number of Fades é 0
        if not np.any(below_threshold):
            NoF = 0
        else:
            # Conversão de Boolean para int (true - 1, false - 0 )
            transitions = np.diff(below_threshold.astype(int))
            #Conta as transições de 0 para 1
            NoF = np.sum(transitions == 1)
            
            # Verifica se o último valor está abaixo do limite, se tiver, considere na conta
            if np.any(below_threshold[-1]): 
                NoF += 1
        
        numfad.append(NoF)
    
    return numfad


def SeparaBlocos(array3D):
    res = []
    for array2D in array3D:
        auxres = array2D[:, 6]
        piso = len(auxres) // 3000
        auxres = auxres[:piso * 3000].reshape((piso, 3000))
        res.append(auxres)
    return res

def LeitorTXT(arquivo):
    matriz = []
    with open(arquivo, "r") as textFile:
        for line in textFile:
            info = [float(item.strip()) for item in line.split(',')]
            col7 = info[4]**2 + info[5]**2
            info.insert(6, col7)
            matriz.append(info)
    
    matriz = np.array(matriz, dtype='f8')
    unq = np.unique(matriz[:, 1:3], axis=0)
    temp = []

    for unique_val in unq:
        indices = np.where((matriz[:, 1] == unique_val[0]) & (matriz[:, 2] == unique_val[1]))[0]
        temp.append(matriz[indices, :])
        
    return temp, unq

if __name__ == "__main__":
    array3D, unq = LeitorTXT("../Desktop/test3.txt")
    
    array3D = SeparaBlocos(array3D)
    fc = fadingCounter(array3D, 15)
    
    for i, fcv in enumerate(fc):
        print(f"fc[{i}]:{fcv}")