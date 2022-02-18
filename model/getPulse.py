from datetime import time
import os
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, butter, lfilter, filtfilt
import numpy
import math


def normalizeData(data : list):
    maxv = max(data)
    minv = min(data)

    res = []
    for i in data:
        res.append((i - minv)/(maxv - minv))

    return res


def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y


def butter_highpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='high', analog=False, output='ba')

    return b, a


def butter_highpass_filter(data, cutoff, fs, order=5):
    b, a = butter_highpass(cutoff, fs, order=order)
    y = filtfilt(b, a, data)
    return y


def PCA_exp():
    pass


def getPulse_simplePeaks(timeData: list, pulseData: list):
    # Cuántos segundos hay entre el inicio y el final de la grabación
    elapsedTime = timeData[-1] - timeData[0]

    # Frecuencia de grabación, cuántos valores por segundo - Hertz
    curr_hz = len(pulseData)/elapsedTime

    # Normalización
    pulseDataТ = normalizeData(pulseData)

    # Contar el número de picos en el gráfico
    peaks, _ = find_peaks(pulseDataТ, distance=4)
    
    pulse = len(peaks)*(60/curr_hz)
    return pulse


def getPulse_cutLowFreq(timeData: list, pulseData: list, currentPulse):
    normalizeData(pulseData)

    # utilizando dos tiempos unix de inicio y fin
    elapsedTime = timeData[-1] - timeData[0]

    # frecuencia de muestreo
    fs = len(pulseData)/elapsedTime

    # frecuencia que debemos desechar mediante el filtrado
    lowcut = (fs / 3) - 1

    # quitar los resultados de baja probabilidad
    max_bpm = 170
    max_bpm_per_sec = max_bpm / fs
    max_beats_spreading_in_one_sec = int(fs / max_bpm_per_sec) - 1
    param = int(math.fabs(fs - max_bpm_per_sec) * lowcut / 2) - max_beats_spreading_in_one_sec
    if param < 1:
        return getPulse_cutLowFreq_ex()

    filteredPulseData = pulseData
    # Debido a un error en la función de la biblioteca, tuvo que ser omitido.
    if currentPulse is 'Procesando..':
        filteredPulseData = butter_highpass_filter(pulseData, lowcut, fs=fs, order=4)

    # ajuste básico de hiperparámetros aquí
    peaks, _ = find_peaks(filteredPulseData, distance=param)
    newPulse = int(len(peaks) * 60 / fs)
    if str(currentPulse).isnumeric():
        delta = (newPulse - currentPulse) / param
        currentPulse += delta
        return int(currentPulse)
    else:
        return int(newPulse)


def getPulse_cutLowFreq_ex():
    files = os.listdir(path="./pulseDataRaw")
    ret = 0

    for filename in files:

        rawData = pd.read_csv("./pulseDataRaw/{}".format(filename), sep=",")
    
        timeData = rawData['x'].to_list()
        pulseData = rawData['y'].to_list()

        pulseDataN = normalizeData(pulseData)

        # utilizando dos tiempos unix de inicio y fin
        elapsedTime = timeData[-1] - timeData[0]
    
        # frecuencia de muestreo
        fs = len(pulseData)/elapsedTime

        # frecuencia que debemos desechar mediante el filtrado
        lowcut = (fs / 3) - 1

        #plt.figure(1)
        #plt.clf()

        # cortar los resultados de baja probabilidad
        max_bpm = 170
        max_bpm_per_sec = max_bpm / fs
        max_beats_spreading_in_one_sec = int(fs / max_bpm_per_sec) - 1

        #plt.plot(timeData, pulseDataN, label='Noisy signal')

        filteredPulseData = butter_highpass_filter(pulseData, lowcut, fs, order=4)

        #plt.plot(timeData, filteredPulseData, label='Filtered signal')

        # ajuste básico de hiperparámetros aquí
        peaks, _ = find_peaks(filteredPulseData, distance=max_beats_spreading_in_one_sec)
        #print("Pulse is:", int(len(peaks)*(60/fs)))
        ret += len(peaks) * 60 / fs
        #for i in range(len(peaks)):
        #    plt.plot(timeData[peaks[i]], filteredPulseData[peaks[i]], "x")

        #plt.grid(True)
        #plt.axis('tight')
        #plt.legend(loc='upper left')

        # Mostrar gráfico auxiliar - para aclarar los cálculos
        #plt.show()
    if not ret:
        return None
    return ret / len(files)


def getPulse_enchanced_ex2():
    # Fallo: un filtro de este tipo requiere una alta frecuencia de lectura de la señal
    files = os.listdir(path="../pulseDataRaw")

    for filename in files:

        rawData = pd.read_csv("./pulseDataRaw/{}".format(filename), sep=",")
    
        timeData = rawData['x'].to_list()
        pulseData = rawData['y'].to_list()
        
        # utilizando dos tiempos unix de inicio y fin
        elapsedTime = timeData[-1] - timeData[0]
    
        # frecuencia de muestreo
        #fs = len(pulseData)/elapsedTime
    
        fs = 20

        # frecuencias que debemos desechar mediante el filtrado
        lowcut = 5
        highcut = 7

        plt.figure(1)
        plt.clf()

        plt.plot(timeData, pulseData, label='Noisy signal')

        filteredPulseData = butter_bandpass_filter(pulseData, lowcut, highcut, fs, order=6)

        plt.plot(timeData, filteredPulseData, label='Filtered signal')
        plt.grid(True)
        plt.axis('tight')
        plt.legend(loc='upper left')

        plt.show()


def getPulse_enchanced_ex():
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.signal import freqz

    # Velocidad de muestreo y frecuencias de corte deseadas (en Hz).
    fs = 5000.0
    lowcut = 500.0
    highcut = 1250.0

    # Traza la respuesta en frecuencia para unos cuantos órdenes diferentes.
    plt.figure(1)
    plt.clf()
    for order in [3, 6, 9]:
        b, a = butter_bandpass(lowcut, highcut, fs, order=order)
        w, h = freqz(b, a, worN=2000)
        plt.plot((fs * 0.5 / np.pi) * w, abs(h), label="order = %d" % order)

    plt.plot([0, 0.5 * fs], [np.sqrt(0.5), np.sqrt(0.5)],
             '--', label='sqrt(0.5)')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Gain')
    plt.grid(True)
    plt.legend(loc='best')

    # Filtrar una señal ruidosa.
    T = 0.05
    nsamples = T * fs
    t = np.linspace(0, T, int(nsamples), endpoint=False)
    a = 0.02
    f0 = 600.0
    x = 0.1 * np.sin(2 * np.pi * 1.2 * np.sqrt(t))
    x += 0.01 * np.cos(2 * np.pi * 312 * t + 0.1)
    x += a * np.cos(2 * np.pi * f0 * t + .11)
    x += 0.03 * np.cos(2 * np.pi * 2000 * t)
    plt.figure(2)
    plt.clf()
    plt.plot(t, x, label='Noisy signal')

    y = butter_bandpass_filter(x, lowcut, highcut, fs, order=6)
    plt.plot(t, y, label='Filtered signal (%g Hz)' % f0)
    plt.xlabel('time (seconds)')
    plt.hlines([-a, a], 0, T, linestyles='--')
    plt.grid(True)
    plt.axis('tight')
    plt.legend(loc='upper left')

    plt.show()


def exampleFunc():
    # método de ejemplo que trabaja con datos del directorio ./pulseDataRaw
    # allí se encuentran los datos de mayor calidad recogidos mediante PPG o BCG
    # método que utiliza la cámara web
    files = os.listdir(path="../pulseDataRaw")

    for filename in files:

        rawData = pd.read_csv("./pulseDataRaw/{}".format(filename), sep=",")
    
        timeData = rawData['x'].to_list()
        pulseData = rawData['y'].to_list()

        print("Pulse2 is:", getPulse_simplePeaks(timeData, pulseData))

        elapsedTime = timeData[-1] - timeData[0]
        print(elapsedTime)

        curr_hz = len(pulseData)/elapsedTime

        pulseData2 = normalizeData(pulseData)
        # print(pulseData2)

        peaks, _ = find_peaks(pulseData, distance=4)
        print("Pulse is:", len(peaks)*(60/curr_hz))
        plt.plot(pulseData)
        
        # plt.plot(peaks, pulseData2[peaks], "x")
        # Lo de arriba no funciona
        # Se sustituye por  un ciclo simple

        for i in range(len(peaks)):
            plt.plot(peaks[i], pulseData[peaks[i]], "x")
        plt.show()


def getPulse(heartBeatTimes, heartBeatValues, currentPulse):
    return getPulse_cutLowFreq(heartBeatTimes, heartBeatValues, currentPulse)



'''
    como datos para cada gráfico, obtenemos datos en dos ejes:
    1 - las unidades condicionales, que representan los valores de la cantidad compleja, por el cambio en
    que determinamos la frecuencia cardíaca de una persona
    2 - tiempo, en el que hemos registrado un valor correspondiente al índice
    valor, en formato de tiempo unix (o número de segundos desde 1.1.1970)
        
    Hay tres columnas en los archivos .csv: índice | tiempo | valor de la variable aleatoria
        
    Una pequeña nota técnica: el valor se llama AVANZADO porque representa
    es un valor basado en las propiedades de color de la imagen utilizando
    diferentes métodos. Podemos utilizar tanto obtener el color medio de alguna parte de la imagen en 
    de la imagen en B/N o sólo el canal verde, que según 
    algunas fuentes indican una preferencia por el método PPG
        
    No la PPG (fotopletismografía) sino la BCG (balistocardiografía).
    Esta es más compleja pero según algunos estudios y artículos
    Es más preciso pero tiene más métodos
    para filtrar los datos significativos:
    1. Necesitamos realizar la tarea de rastrear algunas partes de la cara de la persona, y 
    pista arriba y abajo, a lo largo de las coordenadas verticales.
    (Esto se debe a que la cabeza se tambalea ligeramente por la respiración y los latidos del corazón,
    predominantemente en la dirección vertical, los experimentos han demostrado que es
    El movimiento hacia arriba y hacia abajo es el menos ruidoso, independientemente de los hiperparámetros).
    2. Filtrar los cambios resultantes de los datos en el tiempo por la frecuencia
    características. Dentro de los límites del artículo, tomamos valores de 20 a 200 hercios, porque el pulso
    se encuentra aproximadamente en este rango. Lo lamentable es que la respiración, de la que intentamos alejarnos
    que tratamos de evitar, permanece en cierta medida después de filtrar en el
    gama.
    3. Aplicación del PCA (método de análisis de componentes principales).
    Suele aplicarse como parte de la reducción de la cantidad de datos de entrada mediante la eliminación de
    La dimensión más insignificante de los datos. Aquí lo utilizamos para obtener el
    vectores de datos e identificar entre ellos el que contiene la mayoría de los datos sobre
    movimiento de la cabeza debido a los latidos del corazón.
    4. A continuación, simplemente aplicamos un algoritmo de recuento de picos en el gráfico cuyos parámetros son
    hiperparámetros, que se seleccionan dentro de los límites de los posibles valores de la frecuencia cardíaca.

Traducción realizada con la versión gratuita del traductor www.DeepL.com/Translator
'''