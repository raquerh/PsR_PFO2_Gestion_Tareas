'''
El enunciado menciona un cliente en consola en los objetivos pero no lo describe, así que este es un cliente mínimo con un menú. 
Usa requests.Session() para que la cookie del login se guarde sola y se mande en los pedidos que siguen
'''
# PFO2 - Cliente en consola para la API de tareas
# Programacion sobre Redes - IFTS29

from getpass import getpass
import requests

URL = 'http://127.0.0.1:5000'

# La Session guarda la cookie del login y la manda en los pedidos siguientes
sesion = requests.Session()


def pedir_datos():
    usuario = input('Usuario: ')
    contrasena = getpass('Contraseña: ')
    return {'usuario': usuario, 'contraseña': contrasena}


def registrar():
    respuesta = sesion.post(f'{URL}/registro', json=pedir_datos())
    print(respuesta.status_code, respuesta.json())


def iniciar_sesion():
    respuesta = sesion.post(f'{URL}/login', json=pedir_datos())
    print(respuesta.status_code, respuesta.json())


def ver_tareas():
    respuesta = sesion.get(f'{URL}/tareas')
    print(respuesta.status_code, respuesta.text)


def main():
    while True:
        print('\n1. Registrarse')
        print('2. Iniciar sesion')
        print('3. Ver tareas')
        print('0. Salir')
        opcion = input('Opcion: ')

        try:
            if opcion == '1':
                registrar()
            elif opcion == '2':
                iniciar_sesion()
            elif opcion == '3':
                ver_tareas()
            elif opcion == '0':
                break
            else:
                print('Opcion invalida')
        except requests.exceptions.ConnectionError:
            print('No se pudo conectar con el servidor. ¿Esta corriendo?')


if __name__ == '__main__':
    main()

