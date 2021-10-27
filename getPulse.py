from datetime import time
import os
import pandas as pd
import matplotlib.pyplot as plt
import heartpy as hp
from scipy.signal import find_peaks
import numpy


def getPulse_simplePeaks(timeData: list, pulseData: list):
    # Сколько секунд между началом и концом записи
    elapsedTime = timeData[-1] - timeData[0]

    # Частота записи, сколько значений в секунду - Герцы
    curr_hz = len(pulseData)/elapsedTime

    # Нормализация
    pulseDataТ = normalizeData(pulseData)

    # Подсчёт количества пиков на графике
    peaks, _ = find_peaks(pulseDataТ, distance=4)
    
    pulse = len(peaks)*(60/curr_hz)
    return pulse


def normalizeData(data : list):
    maxv = max(data)
    minv = min(data)

    res = []
    for i in data:
        res.append((i - minv)/(maxv - minv))

    return res

if __name__ == "__main__":
    # example method which working with data from ./pulseDataRaw directory
    # there are located the most quality data collected using PPG or BCG
    # method using web camera
    files = os.listdir(path="./pulseDataRaw")

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
        # не знаю почему, но штука выше не работает, хотя в документации описана
        # Я её заменил просто циклом по peaks, расположенным ниже

        for i in range(len(peaks)):
            plt.plot(peaks[i], pulseData[peaks[i]], "x")
        plt.show()




    #     в качестве данных по каждому графику мы получаем данные по двум осям:
    #     1 - условные единицы, представляющие значения сложной величины, по изменению
    #     которой мы определяем частоту пульса человека
    #     2 - время, в которое было зафиксировано одно соответствующее по индексу
    #     значение, в формате unix-time (или количество секунд от 1.1.1970)
        
    #     В .csv файлах три колонки: индекс | время | значение случайной величины
        
    #     Небольшая техническая ремарка: величина названа СЛОЖНОЙ, потому-что представляет
    #     собой значение, полученное на основе цветовых характеристик изображения с применением
    #     различных методов. Мы можем использовать как получение среднего цвета какой-то части 
    #     изображения в ЧБ тонах, так и значение только лишь зелёного канала, что, согласно 
    #     некоторым источникам, более предпочтительно для PPG метода
        
    #     Что касается не PPG (фотоплетизмографии), а BCG (баллистокардиографии)
    #     Эта задача более сложная, но, согласно некоторым исследования и статьям
    #     имеет более большую точность, но располагает большим количеством методов
    #     для фильтрации значимых данных:
    #     1. Нужно выполнить задачу трекинга некоторых частей лица человека, и 
    #     отслеживать перемещения вверх-вниз, по вертикальным координатам
    #     (Обусловлено это тем, что голову от дыхания и от сердцебиения слегка шатает,
    #     преимущественно в вертикальном направлении, эксперименты показывают, что именно
    #     при считывании движений вверх-вниз шумов меньше всего, вне зависимости от гиперпараметров)
    #     2. Нужно отфильтровать полученные изменения данных с течением времени по частотным
    #     характеристикам. В рамках статьи берутся значения от 20 до 200 герц, так как пульс
    #     лежит примерно в этом диапазоне. Досадно, что и дыхание, от влияния на результат
    #     которого мы стремимся уйти, остаётся в той или иной мере после фильтрации в выбранном
    #     диапазоне.
    #     3. Применение PCA (Метод основных компонент, Principal component analisys).
    #     Обычно он применяется в рамках уменьшения количества входных данных с помощью уничтожения
    #     самого незначещего измерения данных. Здесь мы с его помощью получаем самые значащие
    #     вектора данных и выявляем среди них ту, что содержит в себе большую часть данных об
    #     перемещении головы из-за сердечных сокращений.
    #     4. Далее, мы просто применяем алгоритм подсчёта пиков графика, параметры которого являются
    #     гиперпараметрами, подбор которых производится в рамках возможных значений пульса.
