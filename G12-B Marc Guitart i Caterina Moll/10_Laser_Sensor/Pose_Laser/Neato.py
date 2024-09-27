#!/usr/bin/python
# coding: utf8

"""
Imports
"""
import time

"""
Imports de Teclado
"""
import os, sys
import tty
from select import select

"""
Imports de Procesos
"""
from multiprocessing import Process, Queue

import p_Communication as p_Communication
import p_OdometryLaser as p_OdometryLaser
import p_Plot as p_Plot

"""
Clase para recoger solo una tecla sin enter.
"""
class _Getch:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        
        return ch


# Main
def main():
    # Parametros Robot.
    S = 121.5  # en mm
    distancia_L = 0  # en mm
    distancia_R = 0  # en mm
    speed = 0  # en mm/s
    tita_dot = 0
    tiempo = 5
    direccion = 0

    # Creamos las pipes de comunicacion para los procesos.
    # Pipes para el proceso de Comunicaciones.
    in_pC = Queue()
    out_pC = Queue()

    # Pipe para el proceso de Plotear.
    in_pP = Queue()

    # Creamos los procesos.
    print('Create Processes.')
    p_comunicaciones = Process(target=p_Communication.run, args=(in_pC, out_pC,))
    p_odometriaLaser = Process(target=p_OdometryLaser.run, args=(out_pC, in_pC, in_pP,))
    p_plot = Process(target=p_Plot.run, args=(in_pP,))

    # Ejecutamos los procesos.
    print('Start Processes.')
    p_comunicaciones.start()
    p_odometriaLaser.start()
    p_plot.start()

    # Envio de la S
    out_pC.put(S)

    # Esperamos a inicializar procesos.
    print('Wait for processes.')
    time.sleep(5)

    # Terminal para leer del teclado
    in_key = _Getch()

    print("########################")
    print("Speed = " + str(speed))
    print("Tita_dot = " + str(tita_dot))

    if direccion == 0:
        print("Direction: forward.")
    else:
        print("Direction: backward.")

    print("q to exit.")
    print("########################")

    # Tecla a leer.
    tecla = ''
    comando = ''

    # Variables para el gráfico
    data_queue = Queue()  # Cola para almacenar los datos a graficar
    graph_update_interval = 0.1  # Intervalo de actualización del gráfico en segundos
    last_graph_update_time = time.time()  # Tiempo de la última actualización del gráfico

    while tecla != "q":
        # Leemos la tecla.
        print("Write command: ")
        tecla = in_key()

        if tecla == '8' or tecla == '2':
            if tecla == '8':
                speed = speed + 50
            else:
                speed = speed - 50

            if speed >= 0:
                direccion = 0
            else:
                direccion = 1

            if speed == 0:
                comando = 'SetMotor LWheelDisable RWheelDisable'
                in_pC.put(comando)
                comando = 'SetMotor RWheelEnable LWheelEnable'
                in_pC.put(comando)
            else:
                distancia_R = (((speed * pow(-1, direccion)) + (S * tita_dot)) * tiempo) * pow(-1, direccion)
                distancia_L = (((speed * pow(-1, direccion)) + (-S * tita_dot)) * tiempo) * pow(-1, direccion)

                comando = 'SetMotor LWheelDist ' + str(distancia_L) + ' RWheelDist ' + str(
                    distancia_R) + ' Speed ' + str(speed * pow(-1, direccion))
                in_pC.put(comando)

        elif tecla == '4' or tecla == '6':
            if tecla == '4':
                tita_dot = tita_dot + (3.1415 / 10)
            else:
                tita_dot = tita_dot - (3.1415 / 10)

            distancia_R = (((speed * pow(-1, direccion)) + (S * tita_dot)) * tiempo) * pow(-1, direccion)
            distancia_L = (((speed * pow(-1, direccion)) + (-S * tita_dot)) * tiempo) * pow(-1, direccion)

            if speed == 0:
                speed = 50

            comando = 'SetMotor LWheelDist ' + str(distancia_L) + ' RWheelDist ' + str(
                distancia_R) + ' Speed ' + str(speed * pow(-1, direccion))
            in_pC.put(comando)

        elif tecla == '5':
            direccion = 0
            speed = 0
            tita_dot = 0
            distancia_L = 0
            distancia_R = 0

            comando = 'SetMotor LWheelDisable RWheelDisable'
            in_pC.put(comando)
            comando = 'SetMotor RWheelEnable LWheelEnable'
            in_pC.put(comando)

        elif tecla == '1' or tecla == '3':
            if tecla == '1':
                distancia_R = 1000 * tiempo
            else:
                distancia_R = -1000 * tiempo

            distancia_L = -distancia_R

            if speed == 0:
                speed = 50

            comando = 'SetMotor LWheelDist ' + str(distancia_L) + ' RWheelDist ' + str(
                distancia_R) + ' Speed ' + str(speed * pow(-1, direccion))
            in_pC.put(comando)
            
        elif tecla == 'b':
            in_pP.put('borrar')
            print("########################")
            print("Delete map.")
            print("q to exit.")
            print("########################")

        
           

        if tecla == '8' or tecla == '2' or tecla == '6' or tecla == '4' or tecla == '5' or tecla == '1' or tecla == '3':
            print("########################")
            print("Speed = " + str(speed))
            print("Tita_dot = " + str(tita_dot))

            if direccion == 0:
                print("Direction: forward.")
            else:
                print("Direction: backward.")

            print("q to exit.")
            print("########################")

        # Actualizar el gráfico si ha pasado el tiempo suficiente desde la última actualización
        current_time = time.time()
        if current_time - last_graph_update_time >= 5:
            in_pC.put('Laser')
            print("########################")
            print("Laser.")
            print("q to exit.")
            print("########################")
            # Obtener los datos del proceso de odometría/láser
            if not data_queue.empty():
                data = data_queue.get()
                # Enviar los datos al proceso de graficación
                in_pP.put(data)
                # Actualizar el tiempo de la última actualización
                last_graph_update_time = current_time

    # Enviamos mensajes para finalizar los procesos.
    in_pC.put('quit')
    out_pC.put('quit')

    # Esperar a que finalice.
    p_comunicaciones.join()
    p_odometriaLaser.join()

    print("########################")
    print("q to close Plot.")
    print("########################")
    tecla = ''
    while tecla != "q":
        # Leemos la tecla.
        print("Write command: ")
        tecla = in_key()

    in_pP.put('quit')

    # Esperar a que finalice.
    p_plot.join()

    print("\n\n-- END --\n")


# Llamada a la funcion main
if __name__ == '__main__':
    main()
