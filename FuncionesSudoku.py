from random import *
from math import sqrt

def crear_tablero(dimension):
    #Crea una matriz NxN llena de ceros
    return [[0 for _ in range(dimension)] for _ in range(dimension)]

def validar_movimiento(tablero, dimension, fila, columna, numero):
    #Verificar si el número ya existe en la misma fila o columna
    for i in range(dimension):
        if tablero[fila][i] == numero or tablero[i][columna] == numero: #Busca el número en la fila y columna ingresada
            return False #Si lo encuentra en alguna de estas dos, retorna Falso (el movimiento no es válido)

    #Verificar si el número ya existe en la misma región
    tamaño_de_region = int(sqrt(dimension)) #Se calcula el tamaño de la región
    fila_inicio = tamaño_de_region * (fila // tamaño_de_region) #Se calcula la fila de inicio de la región actual
    columna_inicio = tamaño_de_region * (columna // tamaño_de_region) #Se calcula la columna de inicio de la región actual
    #Se busca el número en la región actual
    for i in range(fila_inicio, fila_inicio + tamaño_de_region):
        for j in range(columna_inicio, columna_inicio + tamaño_de_region):
            if tablero[i][j] == numero:
                return False #Si lo encuentra, retorna Falso (el movimiento no es válido)

    return True #Si no lo encuentra en ninguna de las 3, retorna True (el movimiento es válido)

def llenar_tablero(tablero, dimension):
    #Llena el tablero creado con estilo sudoku (no se repiten números en la misma fila, columna ni región)
    numeros_disponibles = list(range(1, dimension + 1)) #Se crea la lista de los números que se pueden incluir en el sudoku

    for fila in range(dimension):
        columna = 0  #Inicia desde la primera columna
        while columna < dimension: #Recorremos cada columna del tablero
            if tablero[fila][columna] == 0: #Si la celda está vacía se hace el proceso
                shuffle(numeros_disponibles) #Se ordena en forma aleatoria la lista de números creada para llenar cada celda
                for numero in numeros_disponibles: #Se escoge un número
                    if validar_movimiento(tablero, dimension, fila, columna, numero): #Se verifica que el número se pueda poner en la celda actual
                        tablero[fila][columna] = numero #Si el movimiento es válido, se coloca el número escogido
                        break
                else:
                    #Si no se puede colocar el número en esta celda, reiniciamos la fila completa
                    for reset_columna in range(dimension):
                        tablero[fila][reset_columna] = 0
                    columna = 0  #Volvemos a la primera columna nuevamente
                    continue #Se repite el proceso hasta llenar el tablero de forma válida
            columna += 1  #Si la celda no está vacía, moverse a la siguiente columna

    return True

def quitar_celdas(tablero, dimension, num_celdas):
    #Quita números de las celdas según la cantidad de celdas a eliminar
    for _ in range(num_celdas):
        while True:
            fila = randint(0, dimension - 1) #Se escoge una fila al azar
            columna = randint(0, dimension - 1) #Se escoge una columna al azar
            if tablero[fila][columna] != 0:
                tablero[fila][columna] = 0 #Si el valor de la celda no es 0 lo cambia a 0
                break

def crear_sudoku(tablero, dimension, nivel):
  #Crea el sudoku según la dificultad escogida
  if dimension == 4: #Para el sudoku 4x4
    if nivel == "Facil":
      quitar_celdas(tablero, dimension, 6)
    elif nivel == "Normal":
      quitar_celdas(tablero, dimension, 9)
    elif nivel == "Dificil":
      quitar_celdas(tablero, dimension, 11)
      
  elif dimension == 9: #Para el sudoku 9x9
    if nivel == "Facil":
      quitar_celdas(tablero, dimension, 31)
    elif nivel == "Normal":
      quitar_celdas(tablero, dimension, 46)
    elif nivel == "Dificil":
      quitar_celdas(tablero, dimension, 61)






