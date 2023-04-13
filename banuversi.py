'''
Diego Campillay Manriquez
Nicolas Palacios Diaz
Ingenieria Civil Informatica
Universidad Andres Bello
CINF 103
'''

from ast import While
import numpy as np
import copy
import sys
from time import time
import pygame
from pygame.locals import *
pygame.init()


#Color de fondo
COLOR_FONDO = (0, 0, 0)

# Setup del juego
FPS = 60 #Frames por segundo
fpsClock = pygame.time.Clock() #Reloj
WINDOW_WIDTH = 800 #Largo pantalla
WINDOW_HEIGHT = 850 #Alto de pantalla
WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT)) #Setear la resolucion
#Nombre aplicacion
pygame.display.set_caption('BanuVersi')
#Cargar imagenes
FONDO = pygame.image.load('Assets/Fondo.png')
PIEZABLANCA = pygame.image.load('Assets/Blanco.png')
PIEZANEGRA = pygame.image.load('Assets/Negro.png')
JUGADA = pygame.image.load('Assets/piezasJugables.png')

#Cargar Texto
FONT = pygame.font.SysFont('Comic Sans MS', 30)
TEXTO_JUGADOR = FONT.render('Turno Jugador',True,(255, 255, 255))
TEXTO_WHITE = FONT.render('Turno Maquina, Pensando...',True,(255, 255, 255))
GANAR = FONT.render('Ganaste viva Banu por siempre!',True,(255, 255, 255))
PERDER = FONT.render('Perdiste... Apreta R para reiniciar',True,(255, 255, 255))

#Columnas
CANTIDAD_COLUMNAS = 8
# Constantes para saber que hay en tablero y para comparar durante el juego (WHITE = IA  BLACK = Jugador)
WHITE = 1
VACIO = 0
BLACK = -1

EMPATE = 2
GANADOR_VAL = 100
DEMO_SEARCH_DEPTH = 5 #Profundidad de busqueda de prueba

# Direcciones posibles donde insertar siguientes fichas
DIRECCIONES = [(-1, -1), (-1, 0), (-1, 1), (0, -1),
              (0, 1), (1, -1), (1, 0), (1, 1)]


#Retorna estado del juego, Ganador, Perdedor o empate

def encontrar_ganador(tablero):
    # Cuenta las fichas para mostrar un ganador
    white_count = np.count_nonzero(tablero == WHITE)
    black_count = np.count_nonzero(tablero == BLACK)
    if white_count > black_count:
        return WHITE
    elif white_count < black_count:
        return BLACK
    return EMPATE

# generar_mov_legal retorna los movimientos posibles

def generar_mov_legal(tablero, turno_white):
    mov_legales = []
    for r in range(CANTIDAD_COLUMNAS):
        for c in range(CANTIDAD_COLUMNAS):
            if tablero[r][c] != VACIO:
                continue
            if puede_capturar(tablero, r, c, turno_white):
                mov_legales.append((r, c))
    return mov_legales



# Verifica capturas posibles en las 8 direcciones


def puede_capturar(tablero, r, c, turno_white):
    for r_delta, c_delta in DIRECCIONES:
        if capturas_en_dir(tablero, r, r_delta, c, c_delta, turno_white):
            return True
    return False

# Verifica capturas cuando la columna y fila estan modificadas con row como row_delta, col como col_delta


def capturas_en_dir(tablero, row, row_delta, col, col_delta, turno_white):
    if (row+row_delta < 0) or (row+row_delta >= CANTIDAD_COLUMNAS):
        return False
    if (col+col_delta < 0) or (col+col_delta >= CANTIDAD_COLUMNAS):
        return False

    # No puede capturar si esta el color enemigo en esa casilla
    color_enemigo = BLACK if turno_white else WHITE
    if tablero[row+row_delta][col+col_delta] != color_enemigo:
        return False

    # Verifica si hay una ficha enemiga en la dirección
    # Si existe una ficha amistosa retorna True
    # Si no False
    color_amistoso = WHITE if turno_white else BLACK
    scan_row = row + 2*row_delta  # fila del primer escaneo de posicion
    scan_col = col + 2*col_delta  # columna del primer escaneo de posicion
    while (scan_row >= 0) and (scan_row < CANTIDAD_COLUMNAS) and (scan_col >= 0) and (scan_col < CANTIDAD_COLUMNAS):
        if tablero[scan_row][scan_col] == VACIO:
            return False
        if tablero[scan_row][scan_col] == color_amistoso:
            return True
        scan_row += row_delta
        scan_col += col_delta
    return False

# Cambia el tablero para representar las piezas capturadas por el movimiento (row,col)


def captura(tablero, row, col, turno_white):
    # Verifica en cada direccion si hay una ficha que se pudo dar vuelta, si es asi empieza a voltearlas
    color_enemigo = BLACK if turno_white else WHITE
    for row_delta, col_delta in DIRECCIONES:
        if capturas_en_dir(tablero, row, row_delta, col, col_delta, turno_white):
            flip_row = row + row_delta
            flip_col = col + col_delta
            while tablero[flip_row][flip_col] == color_enemigo:
                tablero[flip_row][flip_col] = -color_enemigo
                flip_row += row_delta
                flip_col += col_delta
    return tablero

# Logica que retorna el tablero en el estado actual
# El resultado inserta un tablero con la pieza y las piezas que pudieron cambiar de color
# El tablero se copia para posibles busquedas
# Se mueve por coordenadas

def play_mov(tablero, mov, turno_white):
    new_tablero = copy.deepcopy(tablero)
    new_tablero[mov[0]][mov[1]] = WHITE if turno_white else BLACK
    new_tablero = captura(new_tablero, mov[0], mov[1], turno_white)
    return new_tablero

def ver_game_over(tablero):
    white_mov_legales = generar_mov_legal(tablero, True)
    if white_mov_legales: 
        return VACIO
    black_mov_legales = generar_mov_legal(tablero, False)
    if black_mov_legales:
        return VACIO
    return encontrar_ganador(tablero)

# minimax_valor:  Se asume que la ficha WHITE es MAX y la ficha BLACK es MIN
# turno_white Determina quien se tendra que mover en el siguiente turno
# search_depth es para ver la profundidad restante, decreciente por las llamadas recursivas
# alpha y beta son los lazos en jugadas viables usados como en la poda alfa-beta


def minimax_valor(tablero, turno_white, search_depth, alpha, beta):
    if search_depth == 0:
        return np.count_nonzero(tablero == WHITE) - np.count_nonzero(tablero == BLACK)
    state = ver_game_over(tablero)
    if state == EMPATE:
        return 0
    if state == WHITE:
        return GANADOR_VAL
    if state == BLACK:
        return -GANADOR_VAL
    else:
        # Ninguna condicion de juego, sigue bajando por el arbol
        pass

    if turno_white:
        maxScore = -sys.maxsize
        mov_legales = generar_mov_legal(tablero, True)

        if len(mov_legales) == 0:
            maxScore = minimax_valor(tablero, False, search_depth, alpha, beta)

        else:
            for mov in mov_legales:
                # Obtiene el nuevo estado del tablero
                new_tablero = play_mov(tablero, mov, True)
                score = minimax_valor(
                    new_tablero, False, search_depth - 1, alpha, beta)
                maxScore = max(maxScore, score)
                alpha = max(alpha, score)
                if beta <= alpha:
                    break
        return maxScore

    else:
        minScore = sys.maxsize
        mov_legales = generar_mov_legal(tablero, False)

        if len(mov_legales) == 0:
            minScore = minimax_valor(tablero, True, search_depth, alpha, beta)

        else:
            for mov in mov_legales:
                # Obtiene el nuevo estado del tablero
                new_tablero = play_mov(tablero, mov, False)
                score = minimax_valor(
                    new_tablero, True, search_depth - 1, alpha, beta)
                minScore = min(minScore, score)
                beta = min(beta, score)
                if beta <= alpha:
                    break
        return minScore


def imprimir_tablero(tablero):
    printable = {
        -1: "1",
        0: "-",
        1: "2"
    }
    for r in range(CANTIDAD_COLUMNAS):
        line = ""
        for c in range(CANTIDAD_COLUMNAS):
            line += printable[tablero[r][c]]
        print(line)



def inicializar_tablero():
    tablero = np.zeros((CANTIDAD_COLUMNAS, CANTIDAD_COLUMNAS))
    tablero[3][3] = WHITE
    tablero[3][4] = BLACK
    tablero[4][3] = BLACK
    tablero[4][4] = WHITE
    return tablero


def renderizarPiezas(tablero, render,legalTurns):
    y = 0
    for i in tablero:
        x = 0
        for j in i:
            #print([j,x,y])
            if j == 1.0:
                #Transformar tablero a pixeles de pantalla
                render.blit(PIEZABLANCA, (x*100, y*100)) 
            elif j == -1.0:
                render.blit(PIEZANEGRA, (x*100, y*100))
            
            x += 1
        y += 1
    for i in legalTurns:
        render.blit(JUGADA,(i[1]*100,i[0]*100))
        #print(i[0]*100)


def click(posicion_mouse,posibles_jugadas):
    #Transformar entrada de usuario a coordenadas de tablero
    x = posicion_mouse[0]//100 
    y = posicion_mouse[1]//100
    #print([x,y])

    if (y,x) in posibles_jugadas:
        return (y,x)
    return 0


def main():
    loop_juego = True
    TURNO = WHITE
    tablero = inicializar_tablero()
    enJuego = VACIO
    while loop_juego:
        
        WINDOW.fill(COLOR_FONDO)
        WINDOW.blit(FONDO, (0, 0))
        renderizarPiezas(tablero,WINDOW,generar_mov_legal(tablero,False))

        if TURNO != WHITE and enJuego == VACIO:
            WINDOW.blit(TEXTO_JUGADOR, (400-30*13,800))
        if enJuego == WHITE:
            WINDOW.blit(PERDER, (400-30*13,800))
        elif enJuego == BLACK:
            WINDOW.blit(GANAR, (400-30*13,800))

        pygame.display.update()
        fpsClock.tick(FPS)
        enJuego = ver_game_over(tablero)

        #Si el juego aun no termina
        if  enJuego == VACIO:
            if TURNO == WHITE:

                WINDOW.blit(TEXTO_WHITE, (400-30*13,800)) #Mostrar Texto Maquina
                pygame.display.update()
                
                posibles_movimientos = generar_mov_legal(tablero, True)
                if posibles_movimientos:  # si existen posibles movimientos
                    print("Computador pensando...")
                    best_val = float("-inf")
                    best_mov = None
                    for m in posibles_movimientos:
                        new_tablero = play_mov(tablero, m, True)
                        mov_val = minimax_valor(
                        new_tablero, True, DEMO_SEARCH_DEPTH, float("-inf"), float("inf"))
                        if mov_val > best_val:
                            best_mov = m
                            best_val = mov_val
                    tablero = play_mov(tablero, best_mov, True)
                    imprimir_tablero(tablero)
                else:
                    print("Computador no EMPATEne opciones; saltar turno...")
                    
                TURNO = BLACK
                
            elif TURNO == BLACK:
                
                posibles_movimientos = generar_mov_legal(tablero, False)
                player_mov = 0
                if posibles_movimientos:
                    ev = pygame.event.get()
                    for event in ev:
                        if event.type == pygame.MOUSEBUTTONUP:
                            pos = pygame.mouse.get_pos()
                            player_mov = click(pos,posibles_movimientos)
                        elif event.type == QUIT:
                            pygame.quit()
                            sys.exit()
                    if(player_mov != 0):
                        tablero = play_mov(tablero, player_mov, False)
                        imprimir_tablero(tablero)
                        TURNO = WHITE
                else:
                    print("Jugador no EMPATEne opciones; saltar turno...")  
                    TURNO = WHITE
        #Si termino, opcion de apretar R para reiniciar
        else:
            ev = pygame.event.get()
            for event in ev:
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_r:
                        tablero = inicializar_tablero()
            


main()
