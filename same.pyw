#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Copyright Emmanuel Arias Soto emmanuel1412@gmail.com 2013.
	
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import random, pygame, sys
from pygame.locals import *
from copy import deepcopy


############################################### Clase Main ################################################
#        Maneja los eventos del mouse y coordina las representaciones logicas y graficas del juego        #
############################################### Clase Main ################################################

class Main:

	""" Respectivamente: largo y ancho de ventana, largo y ancho del tablero,
	filas y columnas del tablero, espacio entre cuadros y el margen del tablero.
	"""
	MEDIDAS = (600,600,600,600,18,15,1,30)
	LARGO_VENTANA = MEDIDAS[0]
	ANCHO_VENTANA = MEDIDAS[1]
	FPS = 24 # cuadros por segundo, velocidad general del programa
	GANO = '  Felicidades, ganaste'
	PERDIO = '  Perdiste'
	
	# variables para los objetos
	logico = None
	grafico = None
	
	def iniciar(self):
		
		# iniciar el modulo pygame, el objeto FPS y la venatna
		pygame.init()
		FPSCLOCK = pygame.time.Clock()
		SUPERFICIE = pygame.display.set_mode((self.LARGO_VENTANA, self.ANCHO_VENTANA))
		pygame.display.set_caption('SAME')
		
		# crear los objetos de las clases Logico y Grafico
		logico = Logico(self.MEDIDAS[4], self.MEDIDAS[5])
		grafico = Grafico(logico, SUPERFICIE, self.MEDIDAS)
		
		# almacenan las coordenadas del mouse
		mousex = 0 
		mousey = 0 
		
		grafico.iniciarAnimacionJuego()
		
		while True: # loop principal del juego
			mouseClic = False
			
			if not mouseClic:
				SUPERFICIE.fill(logico.getColorFondo())
				grafico.dibujarTablero()
			 
			for evento in pygame.event.get(): # manejador de eventos
				if evento.type == QUIT or (evento.type == KEYUP and evento.key == K_ESCAPE):
					pygame.quit()
					sys.exit()
				elif not mouseClic and evento.type == MOUSEMOTION:
					mousex, mousey = evento.pos
				elif not mouseClic and evento.type == MOUSEBUTTONUP:
					mousex, mousey = evento.pos
					mouseClic = True
					
				
			# comprobar si el mouse esta actualmente en un cuadro
			cuadrox, cuadroy = grafico.getCuadroEnPixel(mousex, mousey)
			
			if cuadrox != None and cuadroy != None and not mouseClic:
				# el mouse esta sobre un cuadro
				grafico.dibujarCuadroIluminado(cuadrox, cuadroy)
			if	cuadrox != None and cuadroy != None and mouseClic:
				# el mouse esta sobre un cuadro e hizo clic
				mouseClic = True
				grafico.dibujarCuadroIluminado(cuadrox, cuadroy)
				if logico.puedeComer(cuadrox, cuadroy):
					# impide que el usuario haga clic mientras que se maneja el evento
					pygame.event.set_blocked( [MOUSEBUTTONUP, MOUSEMOTION] ) 
					logico.comerCuadros(cuadrox, cuadroy)
					grafico.actualizarCuadro(cuadrox, cuadroy)
					logico.ordenarCuadros()
					
					if logico.getJuegoGanado():
						logico.ganoJuego()
						grafico.animacionFinJuego(self.GANO)
						pygame.time.wait(2000)
						logico.nuevoJuego()
						grafico.iniciarAnimacionJuego()
					elif logico.getJuegoTerminado():
						grafico.animacionFinJuego(self.PERDIO)
						pygame.time.wait(2000)
						logico.nuevoJuego()
						grafico.iniciarAnimacionJuego()
					
				# permite que el usuario vuelva a hacer clic
				mouseClic = False
				pygame.event.set_allowed( [MOUSEBUTTONUP, MOUSEMOTION] ) 	
			
				# aqui comprobar si se ha perdido o ganado
			
			pygame.display.update()	
			FPSCLOCK.tick(self.FPS)	
	
	
#############################################  Clase Grafico ##############################################
#                  Pinta la ventana conforme los datos proporcionados por la clase Logico                 # 
############################################### Clase Main ################################################
	
class Grafico:

	BLANCO = (255, 255, 255)
	TIEMPO_ESPERA = 750	
	
	""" Variables asigandas por el constructor. """
	# medidas
	LARGO_VENTANA = None
	ANCHO_VENTANA = None
	LARGO_TABLERO = None
	ANCHO_TABLERO = None
	FILAS_TABLERO = None
	COLUMNAS_TABLERO = None
	ESPACIO = None
	MARGEN = None
	LARGO_CUADRO = None
	ANCHO_CUADRO = None
	
	# objeto de la superficie y la clase Logico
	SUPERFICIE = None
	logico = None
	
	# fuentes
	fuentePuntosJugada = None
	fuentePuntosTotales = None
	fuenteTitulo = None
	
	def __init__(self, logico, superficie, medidas):
		self.logico = logico
		self.SUPERFICIE = superficie
		self.LARGO_VENTANA = medidas[0]
		self.ANCHO_VENTANA = medidas[1]
		self.LARGO_TABLERO = medidas[2]
		self.ANCHO_TABLERO = medidas[3]
		self.FILAS_TABLERO = medidas[4]
		self.COLUMNAS_TABLERO = medidas[5]
		self.ESPACIO = medidas[6]
		self.MARGEN = medidas[7]
		self.LARGO_CUADRO = ( ( self.LARGO_TABLERO - self.MARGEN - self.MARGEN) - (self.ESPACIO * self.COLUMNAS_TABLERO) ) / self.COLUMNAS_TABLERO
		self.ANCHO_CUADRO = ( ( self.ANCHO_TABLERO - self.MARGEN - self.MARGEN) - (self.ESPACIO * self.FILAS_TABLERO) ) / self.FILAS_TABLERO
		
		self.puntosTotales = 0
		self.fuentePuntosJugada = pygame.font.Font('freesansbold.ttf', 14)
		self.fuentePuntosTotales = pygame.font.Font('freesansbold.ttf', 26)
		self.fuenteTitulo = pygame.font.Font('freesansbold.ttf', 34)

	
	""" Crea el titulo y lo agrega al objeto SUPERFICIE. """
	def mostrarTitulo(self):
		izquierda = self.LARGO_TABLERO / 2
		arriba = self.MARGEN / 2
		texto = 'SAME'
		
		superficieTexto = self.fuenteTitulo.render(str(texto), True, self.BLANCO)
		rectanguloTexto = superficieTexto.get_rect()
		rectanguloTexto.center = ( izquierda, arriba )

		self.SUPERFICIE.blit(superficieTexto, rectanguloTexto)
	
	""" Crea el texto con el puntaje y lo agrega al objeto SUPERFICIE. """
	def mostrarPuntosTotales(self, s):
		izquierda = self.MARGEN
		arriba = self.ANCHO_TABLERO - self.MARGEN
		texto = 'Puntos: ' + str( self.logico.getPuntosTotales() ) + s
		
		superficieTexto = self.fuentePuntosTotales.render(str(texto), True, self.BLANCO)
		rectanguloTexto = superficieTexto.get_rect()
		rectanguloTexto.left = izquierda 
		rectanguloTexto.top = arriba

		self.SUPERFICIE.blit(superficieTexto, rectanguloTexto)

	
	""" Convierte las coordenadas de la esquina superior izquierda del cuadro 
	a una coordenada de pixel.
	"""
	def coordEsquinaCuadro(self, cuadrox, cuadroy):
		izquierda = (cuadrox * (self.LARGO_CUADRO + self.ESPACIO)) + self.MARGEN
		arriba = (cuadroy * (self.ANCHO_CUADRO + self.ESPACIO)) + self.MARGEN
		return (izquierda, arriba)
		

	""" Convierte las coordenadas del centro del cuadro a una coordenada de pixel. """
	def coordCentroCuadro(self, cuadrox, cuadroy):
		izquierda = (cuadrox * (self.LARGO_CUADRO + self.ESPACIO)) + self.MARGEN
		arriba = (cuadroy * (self.ANCHO_CUADRO + self.ESPACIO)) + self.MARGEN
		izquierda += self.LARGO_CUADRO/2
		arriba += self.ANCHO_CUADRO/2
		return (izquierda, arriba)

		
	""" Recorre un tablero "imaginario" y devuelve una posicion si la coordenada
	en pixel esta dentro de algun cuadrado, en caso contrario devuelve la
	tupla (None, None).
	""" 	
	def getCuadroEnPixel(self, x, y):
		for cuadrox in range(self.COLUMNAS_TABLERO):
			for cuadroy in range(self.FILAS_TABLERO):
				izquierda, arriba = self.coordEsquinaCuadro(cuadrox, cuadroy)
				dibCuadro = pygame.Rect(izquierda, arriba, self.LARGO_CUADRO, self.ANCHO_CUADRO)
				if dibCuadro.collidepoint(x, y):
					return (cuadrox, cuadroy)
		return (None, None)
	
	
	""" Vuelve a dibujar el cuadro seÃ±alado por los parÃ¡metros pero de un color mÃ¡s claro. """
	def dibujarCuadroIluminado(self, cuadrox, cuadroy):
		cuadrosIluminados = self.logico.previewComer(self.logico.getTableroTemporal(), [], cuadrox, cuadroy)
		for cuadro in cuadrosIluminados:
			izquierda, arriba = self.coordEsquinaCuadro(cuadro[0], cuadro[1])
			pygame.draw.rect(self.SUPERFICIE, self.logico.getColor(cuadro[0], cuadro[1], False), (izquierda, arriba, self.LARGO_CUADRO, self.ANCHO_CUADRO))

			
	""" Se encarga de dibujar el tablero en la superficie de la ventana. """ 
	def dibujarTablero(self):
		for cuadrox in range(self.COLUMNAS_TABLERO):
			for cuadroy in range(self.FILAS_TABLERO):
				izquierda, arriba = self.coordEsquinaCuadro(cuadrox, cuadroy)
				pygame.draw.rect(self.SUPERFICIE, self.logico.getColor(cuadrox, cuadroy, True), (izquierda, arriba, self.LARGO_CUADRO, self.ANCHO_CUADRO))
		self.mostrarTitulo()
		self.mostrarPuntosTotales('')

		
	""" Dibuja la puntuacion en el cuadro del evento clic y espera un momento
	para apreciar el cambio.
	"""
	def actualizarCuadro(self, cuadrox, cuadroy):
		# crea el texto
		izquierda, arriba = self.coordCentroCuadro(cuadrox, cuadroy)
		superficieTexto = self.fuentePuntosJugada.render(str( self.logico.getPuntosJugada() ), True, self.BLANCO)
		rectanguloTexto = superficieTexto.get_rect()
		rectanguloTexto.center = ( izquierda, arriba )
		
		# dibuja el tablero en estado "comido"  y agrega el texto
		self.SUPERFICIE.fill(self.logico.getColorFondo())
		self.dibujarTablero()
		self.SUPERFICIE.blit(superficieTexto, rectanguloTexto)
		self.mostrarPuntosTotales('')
		pygame.display.update()
		pygame.time.wait(self.TIEMPO_ESPERA)


	""" Dibuja el tablero. """
	def iniciarAnimacionJuego(self):
		self.SUPERFICIE.fill(self.logico.getColorFondo())
		self.dibujarTablero()
		pygame.display.update()
		
	""" Cuando el juego ha terminado hace un efecto flash en el fondo y comienza 
	un nuevo juego. """		
	def animacionFinJuego(self, s):
		color1 = self.logico.getColorFondo()
		color2 = self.logico.getColorFondoClaro()

		for i in range(15):
			color1, color2 = color2, color1
			self.SUPERFICIE.fill(color1)
			self.dibujarTablero()
			self.mostrarPuntosTotales(s)
			pygame.display.update()
			pygame.time.wait(300)		
		
		
########################################### Clase Logico ##################################################	
#             Maneja los datos del tablero, lo actualiza y mantiene la puntuacion del jugador             #
############################################### Clase Main ################################################
	
class Logico:

	#                 R    G    B
	ROJO          = (255,   0,   0)
	ROJOCLARO     = (255, 100, 100)
	AZUL          = (  0,   0, 255)
	AZULCLARO     = (100, 100, 255)
	CELESTE       = (  0, 255, 255)
	CELESTEOSCURO = (  0, 155, 155)
	VERDE         = (  0, 255,   0)
	VERDEOSCURO   = (100, 155, 100)
	NEGRO         = (  0,   0,   0)
	GRIS          = (100, 100, 100)
	COLORCOMIDO = NEGRO
	FONDO = NEGRO
	FONDOCLARO = GRIS
	CUADRO_COMIDO = -1 # representa el valor de una casilla de ma matriz comida
	
	# variables asignadas por el constructor
	FILAS_TABLERO = None
	COLUMNAS_TABLERO = None
	tablero = None
	
	cantidadCuadros = None
	puntosJugada = None
	puntosTotales = None
	juegoTerminado = None
	juegoGanado = None
	
	def __init__(self, filas, columnas):
		self.tablero = []
		self.FILAS_TABLERO = filas
		self.COLUMNAS_TABLERO = columnas
		self.generarTablero()
		self.puntosTotales = 0
		self.juegoGanado = False
		self.juegoTerminado = False


	""" Se encarga de crear una lista de listas con los datos del tablero. """
	def generarTablero(self):
		self.tablero = []
		for x in range(self.COLUMNAS_TABLERO):
			columna = []
			for y in range(self.FILAS_TABLERO):
				columna.append(random.randrange(4))
			self.tablero.append(columna)
			
			
	""" Devuelve la matriz con los datos del tablero. """
	def getTablero(self):
		return self.tablero
		
		
	""" Devuelve una copia de la matriz. """
	def getTableroTemporal(self):
		return deepcopy(self.tablero)
		
		
	""" Agrega el bonus de 1000 puntos al total de puntuacion. """	
	def ganoJuego(self):
		self.puntosTotales += 1000
		
		
	""" Resetea la puntuacion para empezar un nuevo juego. """
	def resetearPuntosTotales(self):
		self.puntosTotales = 0	
		
		
	""" Devuelve los puntos obtenidos en la jugada actual. """
	def getPuntosJugada(self):
		return self.puntosJugada
	
	
	""" Devuelve los puntos totales del juego. """
	def getPuntosTotales(self):
		return self.puntosTotales
		

	""" Devuelven los boolean que comprueban si el juego terminÃ³. """
	def getJuegoGanado(self):
		return self.juegoGanado
		
	def getJuegoTerminado(self):
		return self.juegoTerminado
		
		
	""" Resetea la puntuacion e inicia un nuevo juego."""	
	def nuevoJuego(self):
		self.resetearPuntosTotales()
		self.generarTablero()
		
		
	"""Devuelve una constante de color segun correspoda con el parÃ¡metro c. """
	def getColor(self, x, y, b):
		if self.tablero[x][y] == 0 and b:
			return self.ROJO
		elif self.tablero[x][y] == 1  and b:
			return self.AZUL
		elif self.tablero[x][y] == 2  and b:
			return self.VERDE
		elif self.tablero[x][y] == 3  and b:
			return self.CELESTE
		if self.tablero[x][y] == 0 and not b:
			return self.ROJOCLARO
		elif self.tablero[x][y] == 1 and not b:
			return self.AZULCLARO
		elif self.tablero[x][y] == 2 and not b:
			return self.VERDEOSCURO
		elif self.tablero[x][y] == 3 and not b:
			return self.CELESTEOSCURO
		return self.COLORCOMIDO
		
		
	""" Devuelve el color que representa a los cuadros comidos. """
	def getColorFondo(self):
		return self.FONDO
		
		
	""" Devuelve un color mas claro para el efecto flash del fondo """
	def getColorFondoClaro(self):
		return self.FONDOCLARO
		
		
	""" Devuelve una lista con los cuadros que se podria comer el usuario pero sin 
	modificar la matriz principal de datos, t es una copia de dicha matriz.
	"""
	def previewComer(self, t, posiciones, cuadrox, cuadroy):
		tableroTemporal = t
		posiciones.append( (cuadrox, cuadroy) )
		color = tableroTemporal[cuadrox][cuadroy]
		tableroTemporal[cuadrox][cuadroy] = self.CUADRO_COMIDO
		if (color != self.CUADRO_COMIDO and cuadrox != 0 and tableroTemporal[cuadrox - 1][cuadroy] == color):
			self.previewComer(tableroTemporal, posiciones, (cuadrox - 1), cuadroy) 
		if (color != self.CUADRO_COMIDO and cuadrox < self.COLUMNAS_TABLERO-1 and tableroTemporal[cuadrox + 1][cuadroy] == color):
			self.previewComer(tableroTemporal, posiciones, (cuadrox + 1), cuadroy) 
		if (color != self.CUADRO_COMIDO and cuadroy != 0 and tableroTemporal[cuadrox][cuadroy - 1] == color):
			self.previewComer(tableroTemporal, posiciones, cuadrox, (cuadroy - 1)) 
		if (color != self.CUADRO_COMIDO and cuadroy < self.FILAS_TABLERO-1 and tableroTemporal[cuadrox][cuadroy + 1] == color):
			self.previewComer(tableroTemporal, posiciones, cuadrox, (cuadroy + 1)) 
		return posiciones;
			
			
	""" Determina si se puede hacer clic en el cuadro. """
	def puedeComer(self, x, y):
		if(self.tablero[x][y] == self.CUADRO_COMIDO):
			return False
		elif (x!=0 and self.tablero[x][y] == self.tablero[x-1][y]):
			return True
		elif (x < self.COLUMNAS_TABLERO-1 and self.tablero[x][y] == self.tablero[x+1][y]):
			return True
		elif (y!=0 and self.tablero[x][y] == self.tablero[x][y-1]):
			return True
		elif (y<self.FILAS_TABLERO-1 and self.tablero[x][y] == self.tablero[x][y+1]):
			return True
		return False

		
	""" Recursivamente busca los cuadros del mismo color que tienen un lado en comun
	empezando el indicado por los parametros, ademas de devolver el numero de cuadros
	que se han encontrado. Modifica directamente la matriz.
	"""	
	def comerCuadro(self, cuadrox, cuadroy):
		cuadros = 1
		color = self.tablero[cuadrox][cuadroy]
		self.tablero[cuadrox][cuadroy] = self.CUADRO_COMIDO
		if (color != self.CUADRO_COMIDO and cuadrox != 0 and self.tablero[cuadrox - 1][cuadroy] == color):
			cuadros += self.comerCuadro(cuadrox - 1, cuadroy)
		if (color != self.CUADRO_COMIDO and cuadrox < self.COLUMNAS_TABLERO-1 and self.tablero[cuadrox + 1][cuadroy] == color):
			cuadros += self.comerCuadro(cuadrox + 1, cuadroy)
		if (color != self.CUADRO_COMIDO and cuadroy != 0 and self.tablero[cuadrox][cuadroy - 1] == color):
			cuadros += self.comerCuadro(cuadrox, cuadroy - 1)
		if (color != self.CUADRO_COMIDO and cuadroy < self.FILAS_TABLERO-1 and self.tablero[cuadrox][cuadroy + 1] == color):
			cuadros += self.comerCuadro(cuadrox, cuadroy + 1)
		return cuadros;
		
		
	""" Luego que se llama a comer la matriz se modifica 'subiendo' los cuadros que 
	se han comido a la parte superior de la columna.
	"""	
	def subirCuadros(self):
		for columna in range(self.COLUMNAS_TABLERO):
			c = self.FILAS_TABLERO - 1
			for fila in range(self.FILAS_TABLERO-1, -1, -1):
				if (self.tablero[columna][fila] != self.CUADRO_COMIDO):
					self.tablero[columna][c] = self.tablero[columna][fila]
					c -= 1
					
			while c >= 0:
				self.tablero[columna][c] = self.CUADRO_COMIDO
				c -= 1
			
			
	""" Por ultimo luego de subir los cuadros se verifica si han quedado columnas comidos
	y se pasan estas al final del tablero.
	"""		
	def moverColumnas(self):
		for columna in range(self.COLUMNAS_TABLERO-1, -1, -1):
			if(self.tablero[columna][self.FILAS_TABLERO-1] == self.CUADRO_COMIDO):
				for columnaMover in range(columna, self.COLUMNAS_TABLERO-1):
					for fila in range(self.FILAS_TABLERO):
						self.tablero[columnaMover][fila] = self.tablero[columnaMover+1][fila]
						
				for filaComida in range(self.FILAS_TABLERO):
					self.tablero[self.COLUMNAS_TABLERO-1][filaComida] = self.CUADRO_COMIDO
			
			
	""" Come los respectivos cuadros del tablero y calcula la cantidad de puntos. """
	def comerCuadros(self, cuadrox, cuadroy):
		cantidadCuadros = self.comerCuadro(cuadrox, cuadroy)
		self.puntosJugada = int( (cantidadCuadros * (cantidadCuadros-1) / 2) )
		self.puntosTotales += self.puntosJugada
		
		
	""" Ordena la matriz luego de llamarse a comerCuadros(). """	
	def ordenarCuadros(self):
		self.subirCuadros()
		self.moverColumnas()
		self.comprobarJuego()
		
	
	""" Comprueba si no hay mas jugadas o si ya se comio todo el tablero """
	def comprobarJuego(self):
		self.juegoTerminado = True;
		controlColumna = 0
		controlFila = self.FILAS_TABLERO-1
		while self.juegoTerminado and controlColumna < self.COLUMNAS_TABLERO-1: 
			while self.juegoTerminado and controlFila > 0:
				if ( self.tablero[controlColumna][controlFila] != self.CUADRO_COMIDO and self.tablero[controlColumna][controlFila] ==  self.tablero[controlColumna][controlFila-1] ):
					self.juegoTerminado = False
				elif (self.tablero[controlColumna][controlFila] != self.CUADRO_COMIDO and self.tablero[controlColumna][controlFila] == self.tablero[controlColumna+1][controlFila] ):
					self.juegoTerminado = False
				else:
					controlFila -= 1
			controlColumna += 1
			controlFila = self.FILAS_TABLERO-1

		self.juegoGanado = True
		controlColumna = 0
		controlFila = self.FILAS_TABLERO-1
		while self.juegoGanado and controlColumna < self.COLUMNAS_TABLERO-1:
			while self.juegoGanado and controlFila > 0:
				if (self.tablero[controlColumna][controlFila] != self.CUADRO_COMIDO):
					self.juegoGanado = False
				else:
					controlFila -= 1
			controlColumna += 1
			controlFila = self.FILAS_TABLERO-1
			
		
###########################################################################################################	
	

if __name__ == '__main__':
	main = Main()
	main.iniciar()
