import numpy as np
import matplotlib.pyplot as plt
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
exibir_loggings = True

# Dicionário para mapear valores de unq[i][1] para o nome correspondente do sinal
signal_map = {
    0: "GPS_L1CA", 3: "GPS_L2C", 4: "GPS_L5",
    8: "GLO_L1CA", 11: "GLO_L2CA",
    17: "GAL_L1BC", 20: "GAL_E5a", 21: "GAL_E5b", 22: "GAL_AltBOC",
    24: "GEO_L1CA", 25: "GEO_L5",
    6: "QZS_L1CA", 7: "QZS_L2C", 26: "QZS_L5",
    28: "CMP_B1", 29: "CMP_B2"
}

def log_info(message):
    if exibir_loggings:
        logging.info(message)

def LeitorTXT(arquivo):
    matriz = []
    with open(arquivo, "r") as textFile:
        for line in textFile:
            info = [float(item.strip()) for item in line.split(',')]
            col7 = info[4]**2 + info[5]**2
            info.insert(6, col7)
            matriz.append(info)
    
    matriz = np.array(matriz, dtype='f8')
    
    log_info("Matriz original:")
    log_info("  tempo | satelite | tipo sinal | fase | I | Q | I²+Q²")
    log_info(matriz)
    log_info("")
    
    unq = np.unique(matriz[:, 1:3], axis=0)

    log_info("Número de pares únicos:")
    log_info(unq.size // 2)
    log_info("")
    
    log_info("Valores únicos:")
    log_info(unq)
    log_info("")
    
    temp = []
    for unique_val in unq:
        indices = np.where((matriz[:, 1] == unique_val[0]) & (matriz[:, 2] == unique_val[1]))[0]
        temp.append(matriz[indices, :])
        
    return temp, unq

"""Calcula S4 com Separa Blocos

def CalculaS4(array2D):
    res = []
    for sub_array in array2D:
        auxres = sub_array[:, 6]
        piso = len(auxres) // 3000
        auxres = auxres[:piso * 3000].reshape((piso, 3000))
        s4_values = np.std(auxres, axis=1) / np.mean(auxres, axis=1)
        res.append(s4_values)
    return res"""

def CalculaS4(array3D):
    res = []
    for array2D in array3D:
        s4 = np.std(array2D, axis=1) / np.mean(array2D, axis=1)
        res.append(s4)
    return res

def SeparaBlocos(array3D):
    res = []
    for array2D in array3D:
        auxres = array2D[:, 6]
        piso = len(auxres) // 3000
        auxres = auxres[:piso * 3000].reshape((piso, 3000))
        res.append(auxres)
    return res

'''MinDesvanecimento sem tratamento

def MinDesvanecimento(array3D):
    res = []
    for array2D in array3D:
        auxmin = []
        temp = array2D / np.mean(array2D, axis=1, keepdims=True)
        for array in temp:
            minfad = 10 * np.log10(np.min(array))
            auxmin.append(minfad)
        res.append(auxmin)
    return res'''

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


def DecorrelationTime(array3D, matrizS4):
    res = []
    
    # Iterar sobre cada matriz 2D e a matriz correspondente de S4
    for array2D, listaS4 in zip(array3D, matrizS4):
        auxres = []
        
        # Iterar sobre cada linha da matriz 2D e cada linha correspondente em listaS4x
        for row, s4 in zip(array2D, listaS4):
            mean_row = np.mean(row)
            std_row = np.std(row)
            normalized_row = row - mean_row
            
            # Calcular a autocorrelação para cada linha
            cov_ww = np.correlate(normalized_row, normalized_row, mode='full') / (std_row * len(row))
            cov_ww = cov_ww[len(row)-1:]  # Manter apenas os lags não-negativos
            
            # Discriminação do sinal
            s = np.sign(cov_ww - np.exp(-1))
            i1 = np.where(s == -1)[0]
            
            # Calcular tau0
            if s4 < 0.2:
                tau0 = np.nan
            else:
                if len(i1) == 0:
                    tau0 = np.nan
                else:
                    tau0 = 0.02 * i1[0]  # Multiplicar pela frequência de amostragem
                    tau0 = round(tau0, 4)
            
            auxres.append(tau0)
        
        res.append(auxres)
    
    return res

def ScintillationIndex(array3D):
    s4_matrix = []
    minfad_matrix = []
    tau0_matrix = []
    epsilon = 1e-3  # Valor para evitar log(0) e divisões por zero

    for array2D in array3D:
        # Cálculo de S4 para cada linha da matriz 2D
        s4_array = np.std(array2D, axis=1) / np.mean(array2D, axis=1)
        s4_matrix.append(s4_array)
        
        minfad_array = []
        tau0_array = []

        # Normalização de cada linha da matriz 2D pela média da linha
        normalized_2D = array2D / np.mean(array2D, axis=1, keepdims=True)
        
        for row, s4, norm_row in zip(array2D, s4_array, normalized_2D):
            # Cálculo de minfad usando a matriz normalizada
            non_zero_row = norm_row[norm_row != 0]
            min_row = np.min(non_zero_row) if non_zero_row.size > 0 else epsilon
            minfad = 10 * np.log10(min_row)
            minfad_array.append(minfad)

            # Cálculo de tau0 usando a matriz original
            mean_row = np.mean(row)
            std_row = np.std(row)
            normalized_row = row - mean_row
            
            cov_ww = np.correlate(normalized_row, normalized_row, mode='full') / (std_row * len(row))
            cov_ww = cov_ww[len(row)-1:]  # Manter apenas os lags não-negativos
            
            s = np.sign(cov_ww - np.exp(-1))
            i1 = np.where(s == -1)[0]
            
            if s4 < 0.2:
                tau0 = np.nan
            else:
                tau0 = 0.02 * i1[0] if len(i1) > 0 else np.nan
                if not np.isnan(tau0):
                    tau0 = round(tau0, 4)
            
            tau0_array.append(tau0)
        
        minfad_matrix.append(minfad_array)
        tau0_matrix.append(tau0_array)
    
    return s4_matrix, minfad_matrix, tau0_matrix


def PlotaS4(s4, unq):
    for i, s4_values in enumerate(s4):
        # Criação do título do gráfico
        satelite = unq[i][0]
        sinal = signal_map.get(unq[i][1], "Unknown Signal")
        plt.title(f"Satélite {satelite} - Sinal {sinal}")
        
        # Plotagem dos valores e configuração dos eixos
        plt.plot(s4_values)
        plt.xlabel("Amostras")
        plt.ylabel("S4")
        
        # Salvar e mostrar o gráfico
        plt.savefig(f"../../Desktop/img/teste1(s4)/{satelite}x{sinal}.png")
        plt.show()
        
        # Log do salvamento do gráfico
        log_info(f"Gráfico salvo: ../../Desktop/img/teste1(s4)/{satelite}x{sinal}.png")

def PlotaMinfad(minfad, unq):
    for i, minfad_values in enumerate(minfad):
        # Criação do título do gráfico
        satelite = unq[i][0]
        sinal = signal_map.get(unq[i][1], "Unknown Signal")
        plt.title(f"Satélite {satelite} - Sinal {sinal}")
        
        # Plotagem dos valores e configuração dos eixos
        plt.plot(minfad_values)
        plt.xlabel("Amostras")
        plt.ylabel("Minfad")
        
        # Salvar e mostrar o gráfico
        plt.savefig(f"../../Desktop/img/teste1(minfad)/{satelite}x{sinal}.png")
        plt.show()
        
        # Log do salvamento do gráfico
        log_info(f"Gráfico salvo: ../../Desktop/img/teste1(minfad)/{satelite}x{sinal}.png")
        
def plotDB(array3D, unq, matrix_index, row_index):
    # Criação do título do gráfico
    satelite = unq[matrix_index][0]
    sinal = signal_map.get(unq[matrix_index][1], "Unknown Signal")
    plt.title(f"Satélite {satelite} - Sinal {sinal} - {row_index}")

    # Conversão da linha específica para dB
    array_dB = 10 * np.log10(array3D[matrix_index][row_index])

    # Plotagem dos valores em dB e configuração dos eixos
    plt.plot(array_dB)
    plt.xlabel("Amostras")
    plt.ylabel("dB")

    # Salvar e mostrar o gráfico
    plt.savefig(f"../../Desktop/img/teste1(dB)/{satelite}x{sinal}x{row_index}.png")
    plt.show()

    # Log do salvamento do gráfico
    log_info(f"Gráfico salvo: ../../Desktop/img/teste1(dB)/{satelite}x{sinal}.png")


def SalvaTXT(array3D, unq):
    for i, array in enumerate(array3D):
        # Recuperação do nome do sinal baseado no valor de unq[i][1]
        satelite = unq[i][0]
        sinal = signal_map.get(unq[i][1], "Unknown Signal")
        
        # Salvamento do arquivo com o nome modificado
        np.savetxt(f"../../Desktop/safe/6col/{satelite}x{sinal}.txt", array, header="tempo | satelite | tipo sinal | fase | I | Q | I²+Q²", fmt='%.3f')
        log_info(f"Arquivo salvo: ../../Desktop/safe/6col/{unq[i][0]}x{unq[i][1]}.txt")

if __name__ == "__main__":
    array3D, unq = LeitorTXT("../../Desktop/test1.txt")
    #SalvaTXT(array3D, unq)
    array3D = SeparaBlocos(array3D)
    s4 = CalculaS4(array3D)
    #for i, s4_values in enumerate(s4[3]):
    #    log_info(f"s4[3][{i}]={s4_values}")
    #PlotaS4(s4, unq)
    #minfad = MinDesvanecimento(array3D)
    #PlotaMinfad(minfad, unq)
    plotDB(array3D, unq, 3,  40)
    
    
    '''for i, minfad_values in enumerate(minfad):
        log_info(f"index:{i}")
        log_info(minfad_values)'''
    
    logging.info("Processamento finalizado")

