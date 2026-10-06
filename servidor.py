# PFO2 - Sistema de gestion de tareas con API Flask y SQLite
# Programacion sobre Redes - IFTS29

import sqlite3
from flask import Flask, request, session, jsonify
from markupsafe import escape
from werkzeug.security import generate_password_hash, check_password_hash  # libreria para hashear las contraseñas

# Configuracion de la app Flask
app = Flask(__name__)
app.json.ensure_ascii = False  # para que la ñ se vea bien en las respuestas JSON
app.secret_key = 'clave-para-firmar-la-sesion'  # Flask la usa para firmar la cookie de sesion

DB_PATH = 'tareas.db'  # archivo SQLite donde se guardan los usuarios

def conectar_db():
    # Abre una conexion a la base de datos SQLite
    return sqlite3.connect(DB_PATH)

def inicializar_db():
    # Crea la tabla de usuarios si todavia no existe.
    # Se guarda password_hash y no la contraseña, asi la original no queda en la base.
    # El campo usuario es UNIQUE para que no se pueda registrar dos veces el mismo nombre.
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

# POST /registro: crea un usuario nuevo.
# Recibe un JSON con usuario y contraseña, guarda el hash en la base y responde 201.
# Si falta algun dato responde 400, y si el usuario ya existe responde 409.
@app.route('/registro', methods=['POST'])
def registro():
    # Lee el JSON del pedido (si no es un JSON valido, datos queda vacio)
    datos = request.get_json(silent=True) or {}
    usuario = datos.get('usuario')
    contrasena = datos.get('contraseña')

    # Revisa que lleguen los dos datos
    if not usuario or not contrasena:
        return jsonify({'error': 'Faltan datos: usuario y contraseña'}), 400

    # Se guarda el hash, nunca la contraseña en texto plano
    password_hash = generate_password_hash(contrasena)

    # Guarda el usuario en la base. Los ? evitan que lo que escribe el usuario se mezcle con el SQL
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
        conexion.close()  # se cierra siempre, haya error o no

    return jsonify({'mensaje': 'Usuario registrado'}), 201

# POST /login: verifica las credenciales.
# Busca el hash guardado del usuario y lo compara con la contraseña que llego.
# Si coincide guarda el usuario en la sesion y responde 200, si no responde 401.
@app.route('/login', methods=['POST'])
def login():
    # Lee el JSON del pedido
    datos = request.get_json(silent=True) or {}
    usuario = datos.get('usuario')
    contrasena = datos.get('contraseña')

    # Busca en la base el hash guardado de ese usuario
    conexion = conectar_db()
    fila = conexion.execute(
        'SELECT password_hash FROM usuarios WHERE usuario = ?', (usuario,)
    ).fetchone()
    conexion.close()

    # check_password_hash calcula de nuevo el hash de la contraseña y lo compara con el guardado.
    # Mismo mensaje si falla el usuario o la contraseña, para no decir cual de los dos estaba mal
    if fila is None or not check_password_hash(fila[0], contrasena or ''):
        return jsonify({'error': 'Credenciales invalidas'}), 401

    # Guarda el usuario en la sesion (Flask se la manda al cliente en una cookie firmada)
    session['usuario'] = usuario
    return jsonify({'mensaje': 'Login correcto'}), 200

# GET /tareas: muestra el HTML de bienvenida a quien ya inicio sesion.
@app.route('/tareas', methods=['GET'])
def tareas():
    # Si no hay usuario en la sesion es que no hizo login: responde 401
    if 'usuario' not in session:
        return jsonify({'error': 'Tenes que iniciar sesion'}), 401

    # escape evita que se ejecute HTML si el nombre de usuario trae etiquetas
    return f'<h1>Bienvenido, {escape(session["usuario"])}!</h1>'

# Arranque: crea la tabla si hace falta y levanta el servidor (debug=True lo reinicia al guardar cambios)
if __name__ == '__main__':
    inicializar_db()
    app.run(debug=True)
