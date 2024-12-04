'''
Proyecto 2 Taller de Programación
Integrantes:
Luis Felipe Benavides Solórzano
Joan David Castrillo Solano
Isaac Carballo Chacon
'''
# Librerías que se van a utilizar
from FuncionesSudoku import * # Para crear el sudoku
import tkinter as tk # Para crear la interfaz
from tkinter import filedialog # Para el manejo de archivos
from tkinter import messagebox # Para ventanas emergentes
from copy import deepcopy # Para verificar las respuestas del sudoku
import time # Para generar el cronómetro

# Variables globales
ultima_casilla = None
casillas_en_blanco = 0

def cerrar_ventana(): # Función para cerrar la interfaz (con confirmación del usuario)
    '''
    Entradas: ninguna
    Restricciones: ninguna
    Salida: ventana emergente para confirmar el cierre de la interfaz
    '''
    if messagebox.askokcancel("Cerrar SudokuMania", "¿Estás seguro de que quieres cerrar la aplicación?"):
        root.destroy()

def actualizar_cronometro(): # Función para actualizar el cronómetro
    '''
    Entradas: ninguna
    Restricciones: ninguna
    Salida: actualización del cronómetro cada 10 milisegundos, mensaje de tiempo transcurrido cuando se resuelve el sudoku
    '''
    # Definición de variable global
    global tiempo_texto
    # Comprueba si se ha iniciado el cronómetro y está activo
    if tiempo_inicio is not None and cronometro_activo:
        # Calcula el tiempo transcurrido desde el inicio del cronómetro, redondeado a 2 decimales
        tiempo_transcurrido = round(time.perf_counter() - tiempo_inicio, 2)

        # Comprueba si han transcurrido al menos 60 segundos (1 minuto)
        if tiempo_transcurrido >= 60:  
            # Calcula los minutos y segundos
            minutos = int(tiempo_transcurrido // 60)
            segundos = tiempo_transcurrido % 60
            tiempo_texto = f"Tiempo: {minutos} minuto(s) {segundos:.2f} segundos"
        else:
            # Si no ha pasado un minuto, muestra solo los segundos
            tiempo_texto = f"Tiempo: {tiempo_transcurrido:.2f} segundos"
        # Actualiza el texto en el cronómetro
        cronometro.config(text=tiempo_texto)
        # Programa la función para ejecutarse nuevamente después de 10 milisegundos (aumenta la frecuencia de actualización)
        root.after(10, actualizar_cronometro)  

def iniciar_cronometro(): # Función para iniciar el cronómetro
    '''
    Entradas: ninguna
    Restricciones: ninguna
    Salida: cronómetro iniciado
    '''
    # Declaración de variables globales
    global tiempo_inicio, cronometro_activo, cronometro
    tiempo_inicio = time.perf_counter()  # Registra el tiempo actual usando time.perf_counter(), que da una medida de tiempo más precisa
    cronometro_activo = True # Activa el cronómetro 

    if cronometro is not None: # Comprueba si el cronómetro ya ha sido creado
        actualizar_cronometro() # Si el cronómetro ya existe, llama a la función actualizar_cronometro() para mantenerlo actualizado

def detener_cronometro(): # Función para detener el cronómetro
    '''
    Entradas: ninguna
    Restricciones: ninguna
    Salida: cronómetro detenido
    '''
    # Declaración de variable global
    global cronometro_activo
    cronometro_activo = False # Desactiva el cronómetro

def identificar_region(fila, columna, dimension): # Función para identificar la región de la celda actual
    '''
    Entradas: Dimension del sudoku y la posicion de la casilla mediante la fila y columna
    Restricciones: Solo funciona si la matriz es cuadrada
    Salida: Devuelve la region de la casilla mediante la fila y columna
    '''
    region = int(dimension ** 0.5) # Calcula el tamaño de la region
    region_fila = fila // region # Calcula la fila de la region a la que pertenece la casilla
    region_columna = columna // region # Calcula la fila de la region a la que pertenece la casilla
    return region_fila, region_columna

def pintar_region(fila, columna, dimension, color): # Función para pintar la región de la casilla actual
    '''
    Entradas: Dimension del sudoku, fila y columna a pintar, color con el que se va a pintar
    Restricciones: Solo funciona si la matriz es cuadrada
    Salida: La region que se determino con la fila y la columna pintadas del color de entrada
    '''
    region = int(dimension ** 0.5) # Calcula el tamaño de la region
    for i in range(fila * region, (fila + 1) * region): # Itera a través de las filas de la region
        for j in range(columna * region, (columna + 1) * region): # Itera a través de las columnas de la región
            entradas[i][j].config(bg=color) # Cambia el color de fondo de las casillas de la region
    
def sudoku(dimension, dificultad): # Función para generar el sudoku (de cualquier modalidad)
    '''
    Entradas: dimension del sudoku, nivel de dificultad del sudoku
    Restricciones: la dimension debe ser 4 o 9, la dificultad debe ser "Facil", "Normal" o "Dificil"
    Salida: sudoku jugable de la modalidad escogida, junto al cronómetro y botones para verificar la solución, mostrar la solución y guardar el juego
    '''
    # Declaración de variable global
    global entradas, casillas_en_blanco
    entradas = [[None for _ in range(dimension)] for _ in range(dimension)]
    tablero_respuesta = None

    # Limpia el contenido actual de la ventana
    for widget in root.winfo_children():
        widget.destroy()

    tablero = crear_tablero(dimension) # Crear un tablero de Sudoku vacío
    llenar_tablero(tablero, dimension) # Llenar el tablero con números válidos
    tablero_respuesta = deepcopy(tablero) # Crear una copia del tablero con la solución completa
    crear_sudoku(tablero, dimension, dificultad) # Crear un Sudoku jugable con la dificultad especificada

    global cronometro  # Accede a la variable global cronometro
    # Formato del texto en pantalla del cronómetro 
    cronometro = tk.Label(root, text="", font=("Lato", 16), bg='spring green')
    cronometro.place(x=300, y= 2)

    iniciar_cronometro() # Inicia el cronómetro del juego

    def comprobar_solucion(): # Función para verificar si los valores escritos en las celdas son correctos
        '''
        Entradas: ninguna
        Restricciones: ninguna
        Salida: celdas pintadas de un color según el valor ingresado por usuario. verde si es correcto, rojo si es incorrecto.
                si todos los valores son correctos tira un mensaje de éxito
        '''
        casillas_correctas = 0 # Contador para llevar registro de las celdas correctas
        sudoku_correcto = True  # Suponemos que el Sudoku es correcto hasta que encontremos un error

        # Itera a través de todas las filas y columnas del Sudoku
        for fila in range(dimension):
            for columna in range(dimension):
                if entradas[fila][columna]:
                    entrada = entradas[fila][columna] 
                    if isinstance(entrada, tk.Entry):
                        valor_entrada = entrada.get()
                        if valor_entrada:
                            try:
                                numero = int(valor_entrada) #Intenta convertir la entrada en un numero
                                if 1 <= numero <= dimension: #Valida que el numero este dentro del rango
                                    if tablero_respuesta[fila][columna] == numero:
                                        casillas_correctas += 1
                                        entrada.config(bg='lawn green') # Celda correcta
                                    else:
                                        entrada.config(bg='firebrick3') # Celda incorrecta
                                        sudoku_correcto = False
                                else:
                                   #Muestra una ventana emergente indicando entrada invalida
                                   messagebox.showerror("Entrada inválida", "Ingresa un número válido en el rango del tablero.")
                                   entrada.delete(0, 'end') #Borra la entrada invalida
                                   entrada.config(bg='firebrick3')
                                   entrada.focus_set()

                            except ValueError:
                                #Muestra una ventana emergente indicando entrada no valida
                                messagebox.showerror("Entrada inválida", "Ingresa un número válido en el rango del tablero.")
                                entrada.delete(0, 'end') #Borra la entrada invalida
                                entrada.config(bg='firebrick3')
                                entrada.focus_set()
                        else:
                           entrada.config(bg='firebrick3') # Pinta de rojo las que estén vacias
                    else:
                        entrada.config(bg='lightgray') # Deja las que están fijas en gris
        # Verifica que todas las celdas estén llenas
        if casillas_correctas == casillas_en_blanco: 
            if sudoku_correcto:
                # Detiene el cronómetro y calcula el tiempo transcurrido
                detener_cronometro()
                # Muestra un mensaje de éxito con el tiempo transcurrido
                mensaje = "¡Sudoku resuelto correctamente!\n" + tiempo_texto
                messagebox.showinfo("Éxito", mensaje)
                opciones_juego() # Devuelve al usuario a escoger otra opción de juego
            else:
                # Muestra un mensaje de error si el Sudoku está mal resuelto
                messagebox.showerror("Error", "¡Sudoku mal resuelto!")

    def mostrar_solucion(): # Función para mostrar la solución
        '''
        Entradas: ninguna
        Restricciones: ninguna
        Salida: solución del sudoku que se está jugando
        '''
        for fila in range(dimension):
            for columna in range(dimension):
                numero_respuesta = tablero_respuesta[fila][columna]
                if isinstance(entradas[fila][columna], tk.Entry):
                    #Si la casilla actual es una entrada habilita su edicion
                    entradas[fila][columna]['state'] = 'normal'
                    entradas[fila][columna].config(bg='lawn green')
                    entradas[fila][columna].delete(0, 'end')
                    entradas[fila][columna].insert(0, str(numero_respuesta))
                else:
                    #Si la casilla es una etiqueta simplemente cambia el contenido
                    entradas[fila][columna]['text'] = str(numero_respuesta)
                    entradas[fila][columna].config(bg='lawn green')

        detener_cronometro() # Detiene el cronómetro del juego
        messagebox.showinfo("Solución", "Esta era la solución del Sudoku") # Muestra un mensaje informativo
        opciones_juego() # Devuelve al usuario a escoger otra opción de juego

    def guardar_juego(): # Función para guardar el juego actual
        '''
        Entradas: ninguna
        Restricciones: ninguna
        Salida: guarda el sudoku que se está jugando
        '''
        # Se abre un cuadro de diálogo para seleccionar la ubicación y nombre del archivo a guardar
        archivo = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Archivos de texto", "*.txt")])
        if archivo:
            try:
                # Se intenta abrir el archivo seleccionado en modo escritura
                with open(archivo, 'w') as file:
                    # Se escribe la dimensión del juego en el archivo
                    file.write(f"Dimension: {len(entradas)}\n")
                    # Se recorre la matriz 'entradas' que contiene los valores del juego
                    for fila in range(len(entradas)):
                        for columna in range(len(entradas[0])):
                            casilla = entradas[fila][columna]
                            if isinstance(casilla, tk.Entry):
                                valor = casilla.get()
                            elif isinstance(casilla, tk.Label):
                                valor = casilla.cget("text")
                            else:
                                valor = ""

                            if valor:
                                file.write(f"{valor} ") # Se escribe el valor si existe
                            else:
                                file.write("0 ") # Se escribe '0' si no hay valor
                        file.write("\n") # Se agrega un salto de línea al final de cada fila
                    if tablero_respuesta:
                        # Se escribe una etiqueta para marcar el inicio de la sección de tablero de respuesta
                        file.write("TableroRespuesta:\n")
                        # Se recorre la matriz 'tablero_respuesta' que contiene la solución del juego
                        for fila in tablero_respuesta:
                            file.write(" ".join(map(str, fila)) + "\n")  # Se escribe cada fila del tablero respuesta
                # Se muestra un mensaje informativo indicando que el juego se ha guardado correctamente    
                messagebox.showinfo("Guardado", "Juego guardado correctamente.")
                opciones_juego() # Devuelve al usuario a escoger otra opción de juego
            except Exception as e:
                # En caso de error, se muestra un mensaje de error con la descripción del problema
                messagebox.showerror("Error al guardar", f"Error al guardar el juego: {str(e)}")
            detener_cronometro()

    for fila in range(dimension):
        for columna in range(dimension):
            valor = tablero[fila][columna] # Accede a cada valor del tablero
            if valor == 0:
                # Crear un cuadro de entrada para celdas vacías
                entradas[fila][columna] = tk.Entry(root, font=("Lato", 16), width=2, fg='indian red')
                entradas[fila][columna].grid(row=fila, column=columna)
                casillas_en_blanco += 1
            else:
                # Crear un cuadro de entrada para celdas prellenadas
                entradas[fila][columna] = tk.Label(root, text=str(valor), font=("Lato", 16), width=2)
                entradas[fila][columna].grid(row=fila, column=columna)
                entradas[fila][columna].config(bg='lightgray')
  
    def pintar_fila_columna(fila, columna, dimension): #Funcion para pintar la fila y la columna de la casilla a la que se hizo click
        '''
        Entradas: Dimension del tablero, posicion de la casilla clickada mediante su fila y columna
        Restricciones: ninguna
        Salida: Pinta la fila y columna de la casilla a la que se hizo click, y llama a pintar_region para pintar la region de la casilla
        '''
        entrada = entradas[fila][columna]
        global ultima_casilla # Accede a la variable que guarda la posicion que se clicko por ultima vez

        #Restaura el color de fondo de la ultima casilla y su fila y columna
        if ultima_casilla is not None:
            ultima_fila, ultima_columna = ultima_casilla
            entrada.config(bg='white')
            for i in range(dimension):
                entradas[i][ultima_columna].config(bg='white')
                entradas[ultima_fila][i].config(bg='white')

            region_fila, region_columna = identificar_region(ultima_fila, ultima_columna, dimension)
            pintar_region(region_fila, region_columna, dimension, 'white')

        #Colorear la nueva casilla y su respectiva fila, columna y region
        for i in range(dimension):
            entradas[i][columna].config(bg='lightblue')
            entradas[fila][i].config(bg='lightblue')
        region_fila, region_columna = identificar_region(fila, columna, dimension)
        pintar_region(region_fila, region_columna, dimension, 'sky blue')
        ultima_casilla = (fila, columna)
            
    #Asignar la funcion de clic a las casillas
    for fila in range(dimension):
        for columna in range(dimension):
            entrada = entradas[fila][columna]
            entrada.bind("<FocusIn>", lambda event, f=fila, c=columna, d=dimension: pintar_fila_columna(f, c, d))

    # Creación de botón para comprobar la solución
    comprobar = tk.Button(root, text="Verificar", font=("Lato", 16), command=comprobar_solucion, bg='cyan')
    comprobar.place(x=300, y=45)

    # Creación de botón para ver la solución
    solucion = tk.Button(root, text="Mostrar Solución", font=("Lato", 16), command=mostrar_solucion, bg='cyan')
    solucion.place(x=300, y=100)

    # Creación de botón para guardar el sudoku
    guardar = tk.Button(root, text="Guardar", font=("Lato", 16), command=guardar_juego, bg='cyan')
    guardar.place(x=300, y=155)

def nuevo_juego(): # Función para escoger la modalidad del sudoku a jugar
    '''
    Entradas: ninguna
    Restricciones: ninguna
    Salida: menú para elegir que modalidad de sudoku se quiere jugar
    '''
    # Definición de variables globales
    global casillas_correctas, casillas_en_blanco
    casillas_correctas = 0 # Contador para llevar registro de las celdas correctas
    casillas_en_blanco = 0 # Contador para llevar registro de las celdas en blanco
    # Limpia el contenido actual de la ventana
    for widget in root.winfo_children():
        widget.destroy()

    # Creación de un texto en la ventana para indicar que se seleccione la modalidad
    dimension_text = tk.Label(root, text="Seleccione la modalidad a jugar", font=("Lato", 32), bg='spring green')
    dimension_text.place(x=15, y=100)

    # Creación de botones para las modalidades de sudoku 4x4 de diferentes dificultades
    facil_4x4 = tk.Button(root, text="4x4 - Fácil", font=("Lato", 16), command=lambda: sudoku(4, "Facil"), bg='cyan', width=12)
    facil_4x4.place(x=100, y=180)

    normal_4x4 = tk.Button(root, text="4x4 - Normal", font=("Lato", 16), command=lambda: sudoku(4, "Normal"), bg='cyan', width=12)
    normal_4x4.place(x=100, y=230)

    dificil_4x4 = tk.Button(root, text="4x4 - Dificil", font=("Lato", 16), command=lambda: sudoku(4, "Dificil"), bg='cyan', width=12)
    dificil_4x4.place(x=100, y=280)

    # Creación de botones para las modalidades de sudoku 9x9 de diferentes dificultades
    facil_9x9 = tk.Button(root, text="9x9 - Fácil", font=("Lato", 16), command=lambda: sudoku(9, "Facil"), bg='cyan', width=12)
    facil_9x9.place(x=400, y=180)

    normal_9x9 = tk.Button(root, text="9x9 - Normal", font=("Lato", 16), command=lambda: sudoku(9, "Normal"), bg='cyan', width=12)
    normal_9x9.place(x=400, y=230)

    dificil_9x9 = tk.Button(root, text="9x9 - Dificil", font=("Lato", 16), command=lambda: sudoku(9, "Dificil"), bg='cyan', width=12)
    dificil_9x9.place(x=400, y=280)

    # Creación de botón "Atrás" para regresar a la ventana anterior
    atras = tk.Button(root, text="Atrás", font=("Lato", 16), command=opciones_juego, bg='cyan')
    atras.place(x=545, y=360)

def cargar_juego(): # Función para cargar un sudoku guardado
    '''
    Entradas: ninguna
    Restricciones: ninguna
    Salida: sudoku de un archivo cargado por el usuario
    '''
    # Definición de variables globales
    global casillas_en_blanco, entradas, tablero, tablero_respuesta, dimension
    # Limpia el contenido actual de la ventana
    for widget in root.winfo_children():
        widget.destroy()

    # Abre un cuadro de diálogo para seleccionar un archivo con extensión .txt
    archivo = filedialog.askopenfilename(filetypes=[("Sudoku", "*.txt")])
    if archivo:
        try:
            # Abre el archivo seleccionado en modo lectura
            with open(archivo, 'r') as file:
                lineas = file.readlines() # Agarra todas las lineas del archivo
                dimension = 0 # Crea una variable "dimensión" 
                tablero = [] #Inicializa el tablero actual como una lista vacia
                tablero_respuesta = [] #Inicializa el tablero respuesta como una lista vacia
                cargando_respuesta = False # Variable de control para cuando se esté cargando el tablero respuesta
                # Recorre cada línea en el archivo
                for linea in lineas:
                    if "Dimension:" in linea:
                        # Obtiene la dimensión del sudoku desde la línea
                        dimension = int(linea.split(":")[1].strip())
                    elif "TableroRespuesta:" in linea:
                        # Cambia la variable a True para saber que va a guardar la respuesta
                        cargando_respuesta = True
                    else:
                        valores = list(map(int, linea.split())) # Crea una lista de los valores de la linea actual
                        if not cargando_respuesta:
                            if not tablero:
                                tablero = []
                            tablero.append(valores)
                        else:
                            if not tablero_respuesta:
                                tablero_respuesta = []
                            tablero_respuesta.append(valores)
        except Exception as e:
            # En caso de error al cargar el archivo, muestra un mensaje de error
            messagebox.showerror("Error al cargar", f"Error al cargar el juego: {str(e)}")
            return opciones_juego() # Devuelve al usuario a escoger una opción de juego
    else:
        # Si no se seleccionó ningún archivo, también devuelve al usuario a escoger una opción de juego
        return opciones_juego()

    # Creación del cronómetro para el juego guardado
    global cronometro  # Accede a la variable global cronometro
    # Formato del texto en pantalla del cronómetro
    cronometro = tk.Label(root, text="", font=("Lato", 16), bg='spring green')
    cronometro.place(x=300, y= 2)

    iniciar_cronometro() # Inicia el cronómetro del juego

    # Se vuelven a definir las entradas para el sudoku guardado
    entradas = [[None for _ in range(dimension)] for _ in range(dimension)]

    def comprobar_solucion(): # Función para verificar si los valores escritos en las celdas son correctos
        '''
        Entradas: ninguna
        Restricciones: ninguna
        Salida: celdas pintadas de un color según el valor ingresado por usuario. verde si es correcto, rojo si es incorrecto.
                si todos los valores son correctos tira un mensaje de éxito
        '''
        casillas_correctas = 0 # Contador para llevar registro de las celdas correctas
        sudoku_correcto = True  # Suponemos que el Sudoku es correcto hasta que encontremos un error

        # Itera a través de todas las filas y columnas del Sudoku
        for fila in range(dimension):
            for columna in range(dimension):
                if entradas[fila][columna]:
                    entrada = entradas[fila][columna] 
                    if isinstance(entrada, tk.Entry):
                        valor_entrada = entrada.get()
                        if valor_entrada:
                            try:
                                numero = int(valor_entrada) #Intenta convertir la entrada en un numero
                                if 1 <= numero <= dimension: #Valida que el numero este dentro del rango
                                    if tablero_respuesta[fila][columna] == numero:
                                        casillas_correctas += 1
                                        entrada.config(bg='lawn green') # Celda correcta
                                    else:
                                        entrada.config(bg='firebrick3') # Celda incorrecta
                                        sudoku_correcto = False
                                else:
                                   #Muestra una ventana emergente indicando entrada invalida
                                   messagebox.showerror("Entrada inválida", "Ingresa un número válido en el rango del tablero.")
                                   entrada.delete(0, 'end') #Borra la entrada invalida
                                   entrada.config(bg='firebrick3')
                                   entrada.focus_set()

                            except ValueError:
                                #Muestra una ventana emergente indicando entrada no valida
                                messagebox.showerror("Entrada inválida", "Ingresa un número válido en el rango del tablero.")
                                entrada.delete(0, 'end') #Borra la entrada invalida
                                entrada.config(bg='firebrick3')
                                entrada.focus_set()
                        else:
                           entrada.config(bg='firebrick3') # Pinta de rojo las que estén vacias
                    else:
                        entrada.config(bg='lightgray') # Deja las que están fijas en gris
        # Verifica que todas las celdas estén llenas
        if casillas_correctas == casillas_en_blanco: 
            if sudoku_correcto:
                # Detiene el cronómetro y calcula el tiempo transcurrido
                detener_cronometro()
                # Muestra un mensaje de éxito con el tiempo transcurrido
                mensaje = "¡Sudoku resuelto correctamente!\n" + tiempo_texto
                messagebox.showinfo("Éxito", mensaje)
                opciones_juego() # Devuelve al usuario a escoger otra opción de juego
            else:
                # Muestra un mensaje de error si el Sudoku está mal resuelto
                messagebox.showerror("Error", "¡Sudoku mal resuelto!")

    def mostrar_solucion(): # Función para mostrar la solución
        '''
        Entradas: ninguna
        Restricciones: ninguna
        Salida: solución del sudoku que se está jugando
        '''
        for fila in range(dimension):
            for columna in range(dimension):
                numero_respuesta = tablero_respuesta[fila][columna]
                if isinstance(entradas[fila][columna], tk.Entry):
                    #Si la casilla actual es una entrada habilita su edicion
                    entradas[fila][columna]['state'] = 'normal'
                    entradas[fila][columna].config(bg='lawn green')
                    entradas[fila][columna].delete(0, 'end')
                    entradas[fila][columna].insert(0, str(numero_respuesta))
                else:
                    #Si la casilla es una etiqueta simplemente cambia el contenido
                    entradas[fila][columna]['text'] = str(numero_respuesta)
                    entradas[fila][columna].config(bg='lawn green')

        detener_cronometro() # Detiene el cronómetro del juego
        messagebox.showinfo("Solución", "Esta era la solución del Sudoku") # Muestra un mensaje informativo
        opciones_juego() # Devuelve al usuario a escoger otra opción de juego

    def guardar_juego():# Función para guardar el juego actual
        '''
        Entradas: ninguna
        Restricciones: ninguna
        Salida: guarda el sudoku que se está jugando
        '''
        # Se abre un cuadro de diálogo para seleccionar la ubicación y nombre del archivo a guardar
        archivo = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Archivos de texto", "*.txt")])
        if archivo:
            try:
                # Se intenta abrir el archivo seleccionado en modo escritura
                with open(archivo, 'w') as file:
                    # Se escribe la dimensión del juego en el archivo
                    file.write(f"Dimension: {len(entradas)}\n")
                    # Se recorre la matriz 'entradas' que contiene los valores del juego
                    for fila in range(len(entradas)):
                        for columna in range(len(entradas[0])):
                            casilla = entradas[fila][columna]
                            if isinstance(casilla, tk.Entry):
                                valor = casilla.get()
                            elif isinstance(casilla, tk.Label):
                                valor = casilla.cget("text")
                            else:
                                valor = ""

                            if valor:
                                file.write(f"{valor} ") # Se escribe el valor si existe
                            else:
                                file.write("0 ") # Se escribe '0' si no hay valor
                        file.write("\n") # Se agrega un salto de línea al final de cada fila
                    if tablero_respuesta:
                        # Se escribe una etiqueta para marcar el inicio de la sección de tablero de respuesta
                        file.write("TableroRespuesta:\n")
                        # Se recorre la matriz 'tablero_respuesta' que contiene la solución del juego
                        for fila in tablero_respuesta:
                            file.write(" ".join(map(str, fila)) + "\n")  # Se escribe cada fila del tablero respuesta
                # Se muestra un mensaje informativo indicando que el juego se ha guardado correctamente    
                messagebox.showinfo("Guardado", "Juego guardado correctamente.")
                opciones_juego() # Devuelve al usuario a escoger otra opción de juego
            except Exception as e:
                # En caso de error, se muestra un mensaje de error con la descripción del problema
                messagebox.showerror("Error al guardar", f"Error al guardar el juego: {str(e)}")
            detener_cronometro()

    for fila in range(dimension):
        for columna in range(dimension):
            valor = tablero[fila][columna] # Accede a cada valor del tablero
            if valor == 0:
                # Crear un cuadro de entrada para celdas vacías
                entradas[fila][columna] = tk.Entry(root, font=("Lato", 16), width=2, fg='indian red')
                entradas[fila][columna].grid(row=fila, column=columna)
                casillas_en_blanco += 1
            else:
                # Crear un cuadro de entrada para celdas prellenadas
                entradas[fila][columna] = tk.Label(root, text=str(valor), font=("Lato", 16), width=2)
                entradas[fila][columna].grid(row=fila, column=columna)
                entradas[fila][columna].config(bg='lightgray')

    def pintar_fila_columna(fila, columna, dimension): #Funcion para pintar la fila y la columna de la casilla a la que se hizo click
        '''
        Entradas: Dimension del tablero, posicion de la casilla clickada mediante su fila y columna
        Restricciones: ninguna
        Salida: Pinta la fila y columna de la casilla a la que se hizo click, y llama a pintar_region para pintar la region de la casilla
        '''
        entrada = entradas[fila][columna]
        global ultima_casilla #Accede a la variable que guarda la posicion que se clicko por ultima vez

        #Restaura el color de fondo de la ultima casilla y su fila y columna
        if ultima_casilla is not None:
            ultima_fila, ultima_columna = ultima_casilla
            entrada.config(bg='white')
            for i in range(dimension):
                entradas[i][ultima_columna].config(bg='white')
                entradas[ultima_fila][i].config(bg='white')

            region_fila, region_columna = identificar_region(ultima_fila, ultima_columna, dimension)
            pintar_region(region_fila, region_columna, dimension, 'white')

        #Colorear la nueva casilla y su respectiva fila, columna y region
        for i in range(dimension):
            entradas[i][columna].config(bg='lightblue')
            entradas[fila][i].config(bg='lightblue')
        region_fila, region_columna = identificar_region(fila, columna, dimension)
        pintar_region(region_fila, region_columna, dimension, 'sky blue')
        ultima_casilla = (fila, columna)
            
    #Asignar la funcion de clic a las casillas
    for fila in range(dimension):
        for columna in range(dimension):
            entrada = entradas[fila][columna]
            entrada.bind("<FocusIn>", lambda event, f=fila, c=columna, d=dimension: pintar_fila_columna(f, c, d))

     # Creación de botón para comprobar la solución
    comprobar = tk.Button(root, text="Verificar", font=("Lato", 16), command=comprobar_solucion, bg='cyan')
    comprobar.place(x=300, y=45)

    # Creación de botón para ver la solución
    solucion = tk.Button(root, text="Mostrar Solución", font=("Lato", 16), command=mostrar_solucion, bg='cyan')
    solucion.place(x=300, y=100)

    # Creación de botón para guardar el sudoku
    guardar = tk.Button(root, text="Guardar", font=("Lato", 16), command=guardar_juego, bg='cyan')
    guardar.place(x=300, y=155)

def opciones_juego(): # Función para que el usuario escoja la opción de juego
    '''
    Entradas: ninguna
    Restricciones: ninguna
    Salida: ventana para que el usuario escoja la opción de juego
    '''
    # Limpia el contenido actual de la ventana
    for widget in root.winfo_children():
        widget.destroy()

    # Creación de un texto en la ventana para indicar que se seleccione la opción de juego
    opcion = tk.Label(root, text="Escoge una opción", font=("Lato", 38), bg='spring green')
    opcion.place(x=100, y=125)

    # Creación de botón para jugar un nuevo sudoku
    nuevo = tk.Button(root, text="Nuevo Juego", font=("Lato", 16), command=nuevo_juego, bg='cyan')
    nuevo.place(x=135, y=230)

    # Creación de botón para cargar un sudoku de un archivo
    cargar = tk.Button(root, text="Cargar Juego", font=("Lato", 16), command=cargar_juego, bg='cyan')
    cargar.place(x=345, y=230)

    # Creación de botón "Atrás" para regresar a la ventana anterior
    atras = tk.Button(root, text="Atrás", font=("Lato", 16), command=crear_menu_principal, bg='cyan')
    atras.place(x=545, y=360)

def mostrar_instrucciones():  #Función para mostrar las instrucciones
    '''
    Entradas: ninguna
    Restricciones: ninguna
    Salida: ventana emergente con las instrucciones del juego y la interfaz
    '''
    instrucciones = """
    Instrucciones de la aplicación:
    
    1. El objetivo del juego es llenar el tablero con números del 1 al 9 (o del 1 al 4 en un Sudoku 4x4) de manera que no se repitan en ninguna fila, columna o región.
    
    2. Algunas celdas ya están prellenadas, y no puedes cambiar esos números.
    
    3. Debes completar las celdas vacías de manera que se cumplan las reglas del Sudoku.
    
    4. Utiliza el botón "Jugar Sudoku" para comenzar a jugar.

    5. Puedes crear un juego nuevo o cargar uno que hayas guardado anteriormente.
    
    6. Para guardar un juego en progreso, presiona el botón "Guardar" y ponle un nombre al archivo.

    7. Para cargar un juego, presiona en "Cargar Juego" y escoja el archivo que había guardado.

    8. Cuando quiera salir de la aplicación presione "Cerrar".
    
    ¡Diviértete jugando SudokuMania!
    """
    # Creación y formato de la ventana emergente con las instrucciones
    ventana_instrucciones = tk.Toplevel()
    ventana_instrucciones.title("Instrucciones")
    instrucciones = tk.Label(ventana_instrucciones, text=instrucciones, justify='left')
    instrucciones.pack(padx=20, pady=20)

def crear_menu_principal():  # Función que crea el menú principal de la interfaz
    '''
    Entradas: ninguna
    Restricciones: ninguna
    Salida: menú principal de la interfaz
    '''
    # Limpia el contenido actual de la ventana
    for widget in root.winfo_children():
        widget.destroy()

    # Creación de un texto en la ventana con el nombre de la aplicación
    nombre = tk.Label(root, text="SudokuMania", font=("Lato", 48), bg='spring green')
    nombre.place(x=110, y=125)

    # Creación del botón para empezar a jugar
    jugar = tk.Button(root, text="Jugar Sudoku", font=("Lato", 16), command=opciones_juego, bg='cyan')
    jugar.place(x=135, y=230)

    # Creación del botón que despliega las intrucciones
    instrucciones = tk.Button(root, text="Instrucciones", font=("Lato", 16), command=mostrar_instrucciones, bg='cyan')
    instrucciones.place(x=345, y=230)

    # Creación del botón que cierra la aplicación
    cerrar = tk.Button(root, text="Cerrar", font=("Lato", 16), command=cerrar_ventana, bg='firebrick3')
    cerrar.place(x=545, y=360)

# Creación de la ventana para la interfaz
root = tk.Tk()
root.title('SudokuMania')
root.geometry('650x430')
root.configure(bg='spring green')
# Se llama a la función "crear_menu_principal" para generar el menú en la ventana creada
crear_menu_principal()
# Se mantiene actualizada la ventana en un "mainloop"
root.mainloop()

