# PFO2 - Cliente en consola para la API de tareas
# Programacion sobre Redes - IFTS29

from getpass import getpass  # pide la contraseña sin mostrarla en pantalla
import requests

URL = 'http://127.0.0.1:5000'  # direccion donde corre servidor.py

# La Session guarda la cookie del login y la manda en los pedidos siguientes
sesion = requests.Session()

def pedir_datos():
    # Pide usuario y contraseña por consola y los arma con las claves que espera la API
    usuario = input('Usuario: ')
    contrasena = getpass('Contraseña: ')
    return {'usuario': usuario, 'contraseña': contrasena}

def registrar():
    # Opcion 1: manda los datos a POST /registro y muestra el codigo y la respuesta del servidor
    respuesta = sesion.post(f'{URL}/registro', json=pedir_datos())
    print(respuesta.status_code, respuesta.json())

def iniciar_sesion():
    # Opcion 2: manda los datos a POST /login. Si sale bien, la sesion queda guardada en el cliente
    respuesta = sesion.post(f'{URL}/login', json=pedir_datos())
    print(respuesta.status_code, respuesta.json())

def ver_tareas():
    # Opcion 3: pide GET /tareas. Muestra el bienvenido solo si ya se inicio sesion
    respuesta = sesion.get(f'{URL}/tareas')
    print(respuesta.status_code, respuesta.text)

def main():
    # Muestra el menu en un bucle hasta que se elige 0 (salir)
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
            # Pasa cuando el servidor no esta corriendo
            print('No se pudo conectar con el servidor. ¿Esta corriendo?')

if __name__ == '__main__':
    main()
