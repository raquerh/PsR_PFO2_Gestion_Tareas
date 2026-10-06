# PFO2 - Sistema de gestion de tareas con API Flask y SQLite
# Programacion sobre Redes - IFTS29

'''
Los imports de werkzeug.security y markupsafe no hay que instalarlos: vienen con Flask. 
La librería para hashear que pide la consigna es werkzeug.security. 
La secret_key hace falta para usar session más adelante; para este TP alcanza con un texto fijo.
La tabla guarda password_hash y no contraseña: en ningún lado de la base va a quedar la contraseña original. 
El campo usuario es UNIQUE, y eso es lo que después permite detectar un usuario repetido.
'''

import sqlite3
from flask import Flask, request, session, jsonify
from markupsafe import escape
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.json.ensure_ascii = False  # para que la ñ se vea bien en las respuestas JSON
app.secret_key = 'clave-para-firmar-la-sesion'  # Flask la usa para firmar la cookie de sesion

DB_PATH = 'tareas.db'


def conectar_db():
    # Abre una conexion a la base de datos SQLite
    return sqlite3.connect(DB_PATH)


def inicializar_db():
    # Crea la tabla de usuarios si todavia no existe
    conexion = conectar_db()
    conexion.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    conexion.commit()
    conexion.close()

'''
Qué hace cada parte:
get_json(silent=True) devuelve None si el cuerpo no es un JSON válido
el or {} evita que el servidor se rompa en ese caso. 
Si falta el usuario o la contraseña responde 400. 
generate_password_hash arma el hash con un salt aleatorio incluido.
El INSERT usa ?, igual que en el PFO 1, para que lo que escribe el usuario nunca se pegue al SQL. 
Si el usuario ya existe, SQLite lanza IntegrityError y el servidor responde 409. 
El finally cierra la conexión en cualquiera de los casos.
'''
    
@app.route('/registro', methods=['POST'])
def registro():
    datos = request.get_json(silent=True) or {}
    usuario = datos.get('usuario')
    contrasena = datos.get('contraseña')

    if not usuario or not contrasena:
        return jsonify({'error': 'Faltan datos: usuario y contraseña'}), 400

    # Se guarda el hash, nunca la contraseña en texto plano
    password_hash = generate_password_hash(contrasena)

    conexion = conectar_db()
    try:
        conexion.execute(
            'INSERT INTO usuarios (usuario, password_hash) VALUES (?, ?)',
            (usuario, password_hash)
        )
        conexion.commit()
    except sqlite3.IntegrityError:
        # El campo usuario es UNIQUE, asi que falla si ya existe
        return jsonify({'error': 'El usuario ya existe'}), 409
    finally:
        conexion.close()

    return jsonify({'mensaje': 'Usuario registrado'}), 201

'''
El login busca el hash guardado para ese usuario y usa check_password_hash para compararlo con la contraseña que llegó. 
No se puede "des-hashear": la función vuelve a calcular el hash con el mismo salt y compara el resultado. 
Si no existe el usuario o la contraseña no coincide, responde 401 con el mismo mensaje en los dos casos, para no revelar qué usuarios existen. 
Si coincide, guarda el usuario en session: Flask lo convierte en una cookie firmada que el cliente devuelve en cada pedido siguiente. 
Así es como el login "permite acceso a las tareas".
'''

@app.route('/login', methods=['POST'])
def login():
    datos = request.get_json(silent=True) or {}
    usuario = datos.get('usuario')
    contrasena = datos.get('contraseña')

    conexion = conectar_db()
    fila = conexion.execute(
        'SELECT password_hash FROM usuarios WHERE usuario = ?', (usuario,)
    ).fetchone()
    conexion.close()

    # Mismo mensaje si falla el usuario o la contraseña
    if fila is None or not check_password_hash(fila[0], contrasena or ''):
        return jsonify({'error': 'Credenciales invalidas'}), 401

    session['usuario'] = usuario
    return jsonify({'mensaje': 'Login correcto'}), 200

'''
La consigna pide que GET /tareas muestre un HTML de bienvenida, y eso es lo que devuelve. 
Sin sesión responde 401. 
El escape es para que, si alguien se registra con un nombre que tenga etiquetas HTML, el navegador las muestre como texto en lugar de ejecutarlas. 
Como dato, app.run(debug=True) reinicia el servidor cuando guardás cambios.
'''

@app.route('/tareas', methods=['GET'])
def tareas():
    # Solo se puede entrar si hubo un login antes
    if 'usuario' not in session:
        return jsonify({'error': 'Tenes que iniciar sesion'}), 401

    return f'<h1>Bienvenido, {escape(session["usuario"])}!</h1>'

if __name__ == '__main__':
    inicializar_db()
    app.run(debug=True)



