#!/usr/bin/python
#coding: utf8

"""
Imports de Procesos
"""
"""
Imports
"""
import time

import math

"""
Imports de Procesos
"""
from multiprocessing import Queue
from Queue import Empty

def run(queue_in, queue_out, queue_out2):
	
	print "#### Start OdometryLaser Process."
	
	S = float(queue_in.get())
	print "#### OdometryLaser Process: S = " + str(S)

	print '#### OdometryLaser Process: Started.'
	
	x_r_last = 999.9
	y_r_last = 999.9
	tita_dot = 0

	queue_out.put('Odo')

	while True:

		try:
			
			msg = queue_in.get()
			#msg = queue_in.get_nowait()
			#start_total = time.time()

		except Empty:
			
			#print '#### OdometryLaser Process: Nothing.'
			pass
		
		else:
            
			#print "#### OdometryLaser Process: msg -> " + msg

			if msg == 'quit':
				
				break

			elif msg[0] == 'O':
				
				# ODO
				msg = msg[1:]
				#print msg
				
				x_r = 0 # Pos X robot
				y_r = 0 # Pos Y robot

				pos_robot = [] # Vector of 2 positions (x, y of robot)
				
				#########################################################################################################################				
				#start = time.time()
				datos = msg.split(',')
				#print datos

				LeftWheel_PositionInMM = float(datos[8].split('\r')[0])
				RightWheel_PositionInMM = float(datos[12].split('\r')[0])

				tita_dot = (RightWheel_PositionInMM - LeftWheel_PositionInMM) / (2 * S)
				
				dist = (RightWheel_PositionInMM + LeftWheel_PositionInMM) / 2
				
				#print "Dist: " + str(LeftWheel_PositionInMM) + ' _ ' + str(RightWheel_PositionInMM) + ' _ ' + str(dist) + ' _ '+ str(tita_dot)

				x_r = math.cos(math.radians(tita_dot)) * dist
				y_r = math.sin(math.radians(tita_dot)) * dist

				pos_robot.append(y_r)
				pos_robot.append(x_r)

				#print "Pos: " + str(x_r) + ' _ ' + str(y_r)
				#print "Tiempo calculos Odo: " + str(time.time() - start) + " segundos."
				#########################################################################################################################
				
				if x_r_last != x_r or y_r_last != y_r:
					
					queue_out2.put(pos_robot)
					x_r_last = x_r
					y_r_last = y_r
			
			elif msg[0] == 'L':

				# Laser
				msg = msg[1:]
				#print msg

				datos_laser = [] # Vector of 720 or fewer positions always but always pair (x, y)
				
				#########################################################################################################################
				#start = time.time()
				datos = msg.split(',')
				#print datos

				datos_laser_dist = []

				x = 4
				i = 0
				
				while i < 360:
				
					if (float(datos[x]) > 6001 or float(datos[x]) == 0):

						datos_laser_dist.append(0.0)
					
					else:
					
						datos_laser_dist.append(float(datos[x]))

					x = x + 3
					i = i + 1
				
				#print 'Datos Laser Dist (' + str(len(datos_laser_dist)) + '): ' + str(datos_laser_dist)

				i = 0
				while i < len(datos_laser_dist):

					x = (math.cos(math.radians(90 + i + tita_dot)) * datos_laser_dist[i]) + y_r
					y = (math.sin(math.radians(90 + i + tita_dot)) * datos_laser_dist[i]) + x_r
					
					if x != x_r and y != y_r:

						datos_laser.append(x)
						datos_laser.append(y)
					
					i = i + 1

				#print 'Datos Laser(' + str(len(datos_laser)) + '): ' + str(datos_laser)
				#print "\nTiempo desparseo y calculos Laser: " + str(time.time() - start) + " segundos.\n"
				#########################################################################################################################

				queue_out2.put(datos_laser)
			
			queue_out.put('Odo')
			time.sleep(1.75)
			#print "\nTiempo Total p_OdometryLaser: " + str(time.time() - start_total) + " segundos.\n"

	print "#### Finished OdometryLaser Process."