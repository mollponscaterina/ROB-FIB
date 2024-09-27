#!/usr/bin/python
#coding: utf8

"""
Imports de Procesos
"""
"""
Imports
"""
import time as time2

"""
Imports de Procesos
"""
from multiprocessing import Queue
from Queue import Empty

"""
Imports del ploteo
"""
import sys
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
from pyqtgraph.ptime import time

"""
Imports para numero random
"""
from random import randint

def run(queue_in):
	
	print "###### Start Plot Process."

	app = QtGui.QApplication([])
	p = pg.plot()
	p.setWindowTitle('Live Plot')
	p.setInteractive(False)

	mapa_robot = p.plot(pen=None, name="mapa_robot", symbol='o')
	pos_robot = p.plot(pen=None, name="pos_robot", symbol='x')
	mapa_x = []
	mapa_y = []
	pos_robotx = []
	pos_roboty = []

	#last_pos_robotx = 999.0
	#last_pos_roboty = 999.0

	escala = 1000

	timer = QtCore.QTimer()

	def update():

		try:

			msg = queue_in.get()
			#msg = queue_in.get_nowait()
			#start_total = time2.time()

		except Empty:
			
			#print '###### Plot Process: Nothing.'
			pass
		
		else:
            
			#print "###### Plot Process: msg -> " + msg

			if msg == 'quit':
				
				print '###### Plot Process: Close The Window Plotting.'
				timer.stop()
				return
			
			elif msg == 'borrar':

				#start = time2.time()

				del pos_robotx[:]
				del pos_roboty[:]
				del mapa_x[:]
				del mapa_y[:]

				pos_robot.setData(pos_robotx, pos_roboty)
				mapa_robot.setData(mapa_x, mapa_y)

				#print "\nTiempo Borrado Mapa: " + str(time2.time() - start) + " segundos.\n"

			elif len(msg) == 2:
			
				#start = time2.time()

				x_r = float(msg[0])/escala
				y_r = float(msg[1])/escala
					
				pos_robotx.append(x_r)
				pos_roboty.append(y_r)
				
				pos_robot.setData(pos_robotx, pos_roboty)
				
				#print "\nTiempo Plotear Robot: " + str(time2.time() - start) + " segundos.\n"

			else:

				#start = time2.time()
				
				i = 0
				angulo = 0

				while i < len(msg):
				
					x = float(msg[i])/escala
					y = float(msg[i+1])/escala

					mapa_x.append(x)
					mapa_y.append(y)
											
					i = i + 2
					angulo = angulo + 1
									
				mapa_robot.setData(mapa_x, mapa_y)
				
				#print "\nTiempo Plotear Laser: " + str(time2.time() - start) + " segundos.\n"
	    		
		app.processEvents()
		#print "\nTiempo Total p_Plot: " + str(time2.time() - start_total) + " segundos.\n"

	timer.timeout.connect(update)
	timer.start(1)
	
	print '###### Plot Process: Started.'

	if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
		QtGui.QApplication.instance().exec_() 

	print "###### Finished Plot Process."
