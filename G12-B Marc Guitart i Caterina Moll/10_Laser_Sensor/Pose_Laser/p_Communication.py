#!/usr/bin/python
#coding: utf8

"""
Imports
"""
import time

"""
Imports de Procesos
"""
from multiprocessing import Queue
from Queue import Empty

"""
Imports de Serie
"""
import serial

"""
Function to send commands to Neato robot.
Parametros: 
            missatge: Command to send
            temps: delay to recive data
"""
def envia(ser, msg, t, ret):

    global rbuffer
    rbuffer = ''
    resp = ''
    
    ser.flushInput()
    ser.write(msg + chr(10)) 
    time.sleep(t)
    
    if ret:
    	while ser.inWaiting() > 0:
			resp = ser.readline()
			rbuffer = rbuffer + resp
		#resp = ser.read(8192)
		#rbuffer = rbuffer + resp

    return rbuffer 

def run(queue_in, queue_out):

	print "## Start Communication Process."
	
	error = 0

	try:
		ser = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=1)
		ser.flushOutput()
		print '## Communication Process: Created Port Serial'

	except serial.SerialException:

		print '## Communication Process: Error!!!! Port Serial'
		error = 1

	if error == 0:
		# Enviamos comadon al robot para que se ponga en modo test.
		envia(ser, 'TestMode On', 0.2, False)
		print '## Communication Process: Neato TestMode On.'

		#
		envia(ser, 'SetMotor RWheelEnable LWheelEnable', 0.2, False)
		envia(ser, 'GetMotors LeftWheel RightWheel', 0.2, False)

		# Enviamos comando al robot para que encender laser.
		envia(ser, 'SetLDSRotation On', 0.2, False)
		time.sleep(3)
		print '## Communication Process: Laser On.'

		# Enviamos comando al robot para que suene.
		envia(ser, 'PlaySound 1', 0.2, False)

		print '## Communication Process: Started.'

		last_msg = ''
		
		iteraciones = 0

		while True:

			try:

				#msg = queue_in.get()
				msg = queue_in.get_nowait()
				#start_total = time.time() 
				iteraciones = iteraciones + 1
				#print "valor de X: " + str(x)

			except Empty:
				
				#print '## Communication Process: Nothing.'
				#pass
				if last_msg != '' and iteraciones >= 3:
					envia(ser, last_msg, 0.2, False)
					#print last_msg
					x = 0
		
			else:
	            
				#print "## Communication Process: msg -> " + msg

				if msg == 'quit':
					
					break

				elif msg == 'Odo':

					#start = time.time()
					
					msg_odo = envia(ser, "GetMotors", 0.1, True)
					
					#print msg_odo
					
					queue_out.put('O' + msg_odo)

					#print "\nTiempo pedida de Datos Odo: " + str(time.time() - start) + " segundos.\n"

				elif msg == 'Laser':

					#start = time.time()
					
					msg_laser = envia(ser, "GetLDSScan", 0.1, True)
					
					#print msg_laser
					
					queue_out.put('L' + msg_laser)

					#print "\nTiempo pedida de Datos Laser: " + str(time.time() - start) + " segundos.\n"

				else:
					
					last_msg = msg
					envia(ser, last_msg, 0.1, False)
					iteraciones = 0

			#print "\nTiempo Total p_Comunication: " + str(time.time() - start_total) + " segundos.\n"

		envia(ser, 'SetLDSRotation Off', 0.2, False)
		envia(ser, 'TestMode Off', 0.2, False)
		time.sleep(1)

		ser.close()

	print "\n## Finished Communication Process.\n"
