import numpy as np
import matplotlib.pyplot as plt
from scipy.special import gamma

signal_map = {
    0: "GPS_L1CA", 3: "GPS_L2C", 4: "GPS_L5",
    8: "GLO_L1CA", 11: "GLO_L2CA",
    17: "GAL_L1BC", 20: "GAL_E5a", 21: "GAL_E5b", 22: "GAL_AltBOC",
    24: "GEO_L1CA", 25: "GEO_L5",
    6: "QZS_L1CA", 7: "QZS_L2C", 26: "QZS_L5",
    28: "CMP_B1", 29: "CMP_B2"
}

# Função modificada para extrair dados do arquivo
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

# Função para separar dados em blocos
def SeparaBlocos(array3D):
    res = []
    for array2D in array3D:
        auxres = array2D[:, 6]
        piso = len(auxres) // 3000
        auxres = auxres[:piso * 3000].reshape((piso, 3000))
        res.append(auxres)
    return res

# Função para calcular o índice de cintilação s4
def CalculaS4(array3D):
    res = []
    for array2D in array3D:
        s4 = np.std(array2D, axis=1) / np.mean(array2D, axis=1)
        res.append(s4)
    return res

# Função para calcular o mínimo desvanecimento
def MinDesvanecimento(array3D):
    res = []
    epsilon = 1e-3  # Valor de 0,003 para evitar log(0) e divisões por zero
    for sub_array in array3D:
        auxmin = []
        temp = sub_array / np.mean(sub_array, axis=1, keepdims=True)    # Normaliza cada linha da sub-matriz pela média da linha
        for array in temp:
            non_zero_array = array[array != 0]
            min_row = np.min(non_zero_array) if non_zero_array.size > 0 else epsilon
            minfad = 10 * np.log10(min_row)                       # Calcula o mínimo de desvanecimento em dB
            auxmin.append(minfad)
        res.append(auxmin)
    return res

def CalculaAlphaMu(array3D, s4, minfad):
    res = []
    for array2D, alfa, mu in zip(array3D, s4, minfad): #cada satélite tem cálculo de pdf a cada bloco, uso de s4 para alfa e |minfad| para mu
        mu = np.abs(mu)
        x = np.where(array2D == 0, 1e-10, array2D) #Evitar divisão por zero
        alfa = np.reshape(alfa, (-1, 1)) #conversão da array1D em uma array2D com elementos únicos, para permitir broadcasting 
        mu = np.reshape(mu, (-1, 1))  
        coefficient = (2 * mu**mu * alfa**(mu/2)) / gamma(mu)
        pdf = coefficient * x**(alfa * mu - 1) * np.exp(-mu * x**alfa)
        res.append(pdf)
    return res

def PlotPDF(pdf, s4, minfad, matriz3D, unq):
    sats = len(pdf)
    for i in range(sats):
        blocos = len(pdf[i])
        for j in range(5):
            
            plt.figure()
            print(pdf[i][j])
            
            satelite = unq[i][0]
            sinal = signal_map.get(unq[i][1], "Unknown Signal")
            plt.title(f'PDF para Bloco {j+1} - Satélite {satelite} - Sinal {sinal}')
            
            plt.plot(pdf[i][j], matriz3D[i][j], label=f'Bloco {j+1} - α={s4[i][j]:.2f}, μ={abs(minfad[i][j]):.2f}')
            plt.xlabel('Amostras')
            plt.ylabel('Densidade de Probabilidade')
            plt.legend()
            plt.grid(True)
            
            #plt.savefig(f"../../Desktop/img/teste1(pdf)/{satelite}x{sinal}_Bloco{j+1}.png")
            plt.show()


if __name__ == "__main__":
    matriz3D, unq = LeitorTXT("../Desktop/test2.txt")
    print("leitura ok!")
    matriz3D = SeparaBlocos(matriz3D)
    print("separa ok!")
    s4 = CalculaS4(matriz3D)
    print("s4 ok!")
    min_fad = MinDesvanecimento(matriz3D)
    print("minfad ok!")
    pdf = CalculaAlphaMu(matriz3D, s4, min_fad)
    print("pdf ok!")
    PlotPDF(pdf, s4, min_fad, matriz3D, unq)
    print("graf ok!")
