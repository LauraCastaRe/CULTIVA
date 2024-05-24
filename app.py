import os
from flask import Flask, render_template, request,redirect, send_from_directory, url_for,flash,session
from flask_mysqldb import MySQL
import re
from datetime import datetime
from werkzeug.utils import secure_filename


#conexion base de datos
app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'registrosCULTIVARED'
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
mysql = MySQL(app)
app.secret_key='mysecretkey'

#Pagina Inicio
@app.route('/')
def index():
    return render_template('inicio.html')

#Pagina registro de usuario
@app.route('/Registrate')
def registro():
    return render_template('registro.html')

@app.route('/formulario', methods=['GET','POST'])
def form():
    if request.method == 'POST':
        ide = request.form['identificacion']
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        genero = request.form['genero']
        telefono = request.form['telefono']
        email = request.form['email']
        contrasena1 = request.form['contrasena1']
        contrasena2 = request.form['contrasena2']
        rol = request.form['rol']
        
        # Verificar si la cédula ya está registrada
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE id = %s", (ide,))       
        user = cur.fetchone()
        if user:
            alerta = """<script> alert("Esta cedula ya esta registrada");window.location.href = "/Registrate"; </script>"""
            return alerta

        # Verificar si el email ya está registrado
        cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,)) 
        user1 = cur.fetchone()
        if user1:
            alerta = """<script> alert("El email ya esta registrado");window.location.href = "/Registrate"; </script>"""
            return alerta

        # Validar la contraseña
        if len(contrasena1) < 8 or not re.search(r'[A-Z]', contrasena1) or not re.search(r'\d', contrasena1):
            alerta = """<script> alert("La contraseña debe tener por lo menos 8 caracteres, una letra en mayúscula y un número");window.location.href = "/Registrate";</script>"""
            return alerta

        # Verificar la coincidencia de las contraseñas
        if contrasena1 != contrasena2:
            alerta = """<script> alert("Las contraseñas no coinciden");window.location.href = "/Registrate"; </script>"""
            return alerta

        # Insertar el usuario en la base de datos
        cur.execute("INSERT INTO usuarios (ID, nombre, apellido, genero, telefono, email, contrasena1, contrasena2, rol) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (ide, nombre, apellido, genero, telefono, email, contrasena1, contrasena2, rol))
    
        mysql.connection.commit()
        
        alerta = """<script> alert("Usuario registrado correctamente"); window.location.href = "/"; </script>"""
        return alerta

    # Si el método es GET, devolver algo aquí si es necesario
    return render_template("inico.html")

#pagina login de usuario
@app.route('/IniciaSesion')
def iniciar():
    return render_template('login.html')

#verificacion login con bd
@app.route('/login', methods=['GET','POST'])
def log():
    if request.method == 'POST':
        ema = request.form['email']
        contrasena1 = request.form['contrasena1']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE email=%s AND contrasena1=%s", (ema, contrasena1))
        account = cur.fetchone()

        if account:
            
            session['logueado'] = True
            session['email'] = account[5]
            session['rol'] = account[8]
            session['id'] = account[0]

            if session['rol'] == 'Admin':
                alerta = """<script> alert("Bienvenido a CULTIVARED"); window.location.href = "/Administrador"; </script>"""
                return alerta
            elif session['rol'] == 'Vendedor':
                alerta = """<script> alert("Bienvenido a CULTIVARED"); window.location.href = "/Vendedor"; </script>"""
                return alerta
            elif session['rol'] == 'Comprador':
                alerta = """<script> alert("Bienvenido a CULTIVARED"); window.location.href = "/Tienda"; </script>"""
                return alerta
        else:
            alerta = """<script> alert("Usuario o contraseña incorrecta"); window.location.href = "/login"; </script>"""
            return alerta

    return render_template("login.html")

#cierra sesion
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

#vista administrador
@app.route('/Administrador')
def admin():
    if 'logueado' in session and session['logueado']:
        if 'rol' in session:
            rol=session['rol']
            if rol=='Admin':
                cur = mysql.connection.cursor()
                cur.execute('SELECT * FROM usuarios WHERE email = %s', (session['email'],))
                user = cur.fetchone()
                cur.close()
                return render_template('administrador/administrador.html', user=user)
            else:
                if rol=='Vendedor':
                    alerta = """<script> alert("No tienes permisos."); window.location.href = "/Vendedor"; </script>"""
                    return alerta
                elif rol=='Comprador':
                    alerta = """<script> alert("No tienes permisos."); window.location.href = "/Comprador"; </script>"""
                    return alerta 
    else:
        alerta = """<script> alert("Por favor, primero inicie sesión."); window.location.href = "/login"; </script>"""
        return alerta

#crud usuarios
@app.route('/crud')
def crudUsuario():
    if 'logueado' in session and session['logueado']:
        if 'rol' in session:
            rol=session['rol']
            if rol=='Admin':
                cur = mysql.connection.cursor()
                cur.execute('SELECT * FROM usuarios')
                data = cur.fetchall()
                user = cur.fetchone()
                return render_template('/administrador/crud_admin.html', data=data, user=user)
            else:
                if rol=='Comprador':
                    alerta = """<script> alert("No tienes permisos."); window.location.href = "/Comprador"; </script>"""
                    return alerta
                elif rol=='Vendedor':
                    alerta = """<script> alert("No tienes permisos."); window.location.href = "/Vendedor"; </script>"""
                    return alerta 
    else:
        alerta = """<script> alert("Por favor, primero inicie sesión."); window.location.href = "/login"; </script> """
        return alerta

#metodo eliminar de usuarios
@app.route('/eliminar/<int:id>')
def eliminar(id):
    if 'logueado' in session and session['logueado']:
        if 'rol' in session:
            rol=session['rol']
            if rol=='Admin':
                cur = mysql.connection.cursor()
                cur.execute("DELETE FROM usuarios WHERE id = %s", (id,))
                mysql.connection.commit()
                return redirect(url_for('crudUsuario'))
            else:
                if rol=='Comprador':
                    alerta = """<script> alert("No tienes permisos."); window.location.href = "/Comprador"; </script>"""
                    return alerta
                elif rol=='Vendedor':
                    alerta = """<script> alert("No tienes permisos."); window.location.href = "/Vendedor"; </script>"""
                    return alerta 
    else:
        alerta = """<script> alert("Por favor, primero inicie sesión."); window.location.href = "/login"; </script> """
        return alerta
    
#pagina de formulario para editar usuarios
@app.route('/editar/<id>')
def editar(id):
    if 'logueado' in session and session['logueado']:
        if 'rol' in session:
            rol=session['rol']
            if rol=='Admin':
                cur = mysql.connection.cursor()
                cur.execute("SELECT * FROM usuarios WHERE ID = %s", (id,))
                data = cur.fetchall()
                return render_template('/administrador/editarUsuario.html',user=data[0])
            else:
                if rol=='Comprador':
                    alerta = """<script> alert("No tienes permisos."); window.location.href = "/Comprador"; </script>"""
                    return alerta
                elif rol=='Vendedor':
                    alerta = """<script> alert("No tienes permisos."); window.location.href = "/Vendedor"; </script>"""
                    return alerta 
        else:
            alerta = """<script> alert("Por favor, primero inicie sesión."); window.location.href = "/login"; </script> """
            return alerta

#metodo para actualizar en usuarios
@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        genero = request.form['genero']
        telefono = request.form['telefono']
        email = request.form['email']
        contrasena1 = request.form['contrasena1']
        rol = request.form['rol']
        
        cur = mysql.connection.cursor()
        cur.execute("""UPDATE usuarios SET nombre=%s, apellido=%s,
                       genero=%s, telefono=%s, email=%s, contrasena1=%s, 
                       rol=%s WHERE id=%s""", 
                    (nombre, apellido, genero, telefono, email, contrasena1, rol, id))
        mysql.connection.commit()
        
        session['logueado'] = True
        session['email'] = email
        session['rol'] = rol
        

        if rol == 'Admin':
            return redirect(url_for('crudUsuario'))
        elif rol == 'Vendedor':
            return redirect(url_for('vendedor'))
        elif rol == 'Comprador':
            return redirect(url_for('comprador'))

#crud productos
@app.route("/Productos")
def Productos():
    if 'logueado' in session and session['logueado']:
        if 'rol' in session:
            rol=session['rol']
            if rol=='Admin':
                cur = mysql.connection.cursor()
                cur.execute('SELECT * FROM productos')
                data = cur.fetchall()
                cur.execute('SELECT * FROM usuarios WHERE email = %s', (session['email'],))
                user = cur.fetchone()
                return render_template("administrador/productos.html", produ=data,user=user)
            else:
                if rol=='Comprador':
                    alerta = """<script> alert("No tienes permisos."); window.location.href = "/Comprador"; </script>"""
                    return alerta
                elif rol=='Vendedor':
                    Usuario = session['email']
                    cur = mysql.connection.cursor()
                    cur.execute('SELECT * FROM productos WHERE idVendedor = %s', (Usuario,))
                    data = cur.fetchall()
                    cur.execute('SELECT * FROM usuarios WHERE email = %s', (session['email'],))
                    user = cur.fetchone()
                    return render_template('/vendedor/crud_producto.html', produ=data,user=user)
    else:
        alerta = """<script> alert("Por favor, primero inicie sesión."); window.location.href = "/login"; </script> """
        return alerta
         
@app.route('/uploads/<filename>')
def uploaded_file(uploads):
    return send_from_directory(app.config['uploads'], uploads)

#metodo para eliminar productos
@app.route('/eliminarProducto/<int:id>')
def eliminarProdu(id):
    if 'logueado' in session and session['logueado']:
        if 'rol' in session:
            rol=session['rol']
            if rol=='Admin':
                cur = mysql.connection.cursor()
                cur.execute("DELETE FROM productos WHERE idProducto = %s", (id,))
                mysql.connection.commit()
                flash('Producto eliminado correctamente')
                return redirect(url_for('Productos'))
            else:
                if rol=='Comprador':
                    cur = mysql.connection.cursor()
                    cur.execute("DELETE FROM carrito WHERE idP = %s", (id,))
                    mysql.connection.commit()
                    return redirect(url_for('ver_carrito'))
                elif rol=='Vendedor':
                    cur = mysql.connection.cursor()
                    cur.execute("DELETE FROM productos WHERE idProducto = %s", (id,))
                    mysql.connection.commit()
                    return redirect(url_for('Productos'))
    else:
        alerta = """<script> alert("Por favor, primero inicie sesión."); window.location.href = "/login"; </script> """
        return alerta

#pagina para editar productos
@app.route('/editarProducto/<id>')
def editarProdu(id):
    if 'logueado' in session and session['logueado']:
        if 'rol' in session:
            rol=session['rol']
            if rol=='Admin':
                cur = mysql.connection.cursor()
                cur.execute("SELECT * FROM productos WHERE idProducto = %s", (id,))
                data = cur.fetchall()
                return render_template('/administrador/productoEditar.html',produ=data[0])
            else:
                if rol=='Comprador':
                    alerta = """<script> alert("No tienes permisos."); window.location.href = "/Comprador"; </script>"""
                    return alerta
                elif rol=='Vendedor':
                    cur = mysql.connection.cursor()
                    cur.execute("SELECT * FROM productos WHERE idProducto = %s", (id,))
                    data = cur.fetchall()
                    cur.execute('SELECT * FROM usuarios WHERE email = %s', (session['email'],))
                    user = cur.fetchone()
                    return render_template('/vendedor/editarProducto.html',produ=data[0],user=user)
    else:
        alerta = """<script> alert("Por favor, primero inicie sesión."); window.location.href = "/login"; </script> """
        return alerta

#metodo para actualizar en el crud
@app.route('/updateProducto/<id>', methods=['GET','POST'])
def updateProdu(id):
    if request.method == 'POST':
        idProducto = request.form['idProducto']
        nombreProducto = request.form['nombreProducto']
        categoria = request.form['categoria']
        cantidadProducto = request.form['unidades']
        precioProducto = request.form['precio']

        cur = mysql.connection.cursor()
        cur.execute("""UPDATE productos SET idProducto=%s, nombreProducto=%s,
                       categoria=%s, cantidadProducto=%s, precioProducto=%s 
                       WHERE idProducto=%s""",
                    (idProducto, nombreProducto, categoria, cantidadProducto, precioProducto, id))
        mysql.connection.commit()
        flash('Producto actualizado correctamente')
        return redirect(url_for('Productos'))

@app.route("/Vendedor")
def vend():
    if 'logueado' in session and session['logueado']:
        if 'logueado' in session and session['logueado']:
            if 'rol' in session:
                rol=session['rol']
                if rol=='Admin':
                    alerta = """<script> alert("No tienes permisos."); window.location.href = "/Administrador"; </script>"""
                    return alerta
                else:
                    if rol=='Comprador':
                        alerta = """<script> alert("No tienes permisos."); window.location.href = "/Comprador"; </script>"""
                        return alerta
                    elif rol=='Vendedor':
                        cur = mysql.connection.cursor()
                        cur.execute('SELECT * FROM usuarios WHERE email = %s', (session['email'],))
                        user = cur.fetchone()
                        cur.close()
                        return render_template('vendedor/vendedor.html', user=user) 
    else:
        alerta = """<script> alert("Por favor, primero inicie sesión."); window.location.href = "/login"; </script> """
        return alerta

#pagina vendedor
@app.route("/Perfil")
def vendedor():
    if 'logueado' in session and session['logueado']:
        if 'logueado' in session and session['logueado']:
            if 'rol' in session:
                rol=session['rol']
                if rol=='Admin':
                    alerta = """<script> alert("No tienes permisos."); window.location.href = "/Administrador"; </script>"""
                    return alerta
                else:
                    if rol=='Comprador':
                        alerta = """<script> alert("No tienes permisos."); window.location.href = "/Comprador"; </script>"""
                        return alerta
                    elif rol=='Vendedor':
                        cur = mysql.connection.cursor()
                        cur.execute('SELECT * FROM usuarios WHERE email = %s', (session['email'],))
                        user = cur.fetchone()
                        cur.close()
                        return render_template('vendedor/perfil.html', user=user) 
    else:
        alerta = """<script> alert("Por favor, primero inicie sesión."); window.location.href = "/login"; </script> """
        return alerta

#pagina de registar los productoss
@app.route('/RegistraProductos')
def producto():
    if 'logueado' in session and session['logueado']:
        if 'rol' in session:
            rol=session['rol']
            if rol=='Vendedor':
                cur = mysql.connection.cursor()
                mysql.connection.commit()
                cur.execute('SELECT * FROM usuarios WHERE email = %s', (session['email'],))
                user = cur.fetchone()
                alerta="""<script> alert("Producto registrado."); window.location.href = "/Vendedor"; </script>"""
                return render_template('/vendedor/registroProducto.html',user=user)
            else:
                if rol=='Comprador':
                    alerta = """<script> alert("No tienes permisos."); window.location.href = "/Comprador"; </script>"""
                    return alerta
                elif rol=='Admin':
                    alerta = """<script> alert("No tienes permisos."); window.location.href = "/Administrador"; </script>"""
                    return alerta 
    else:
        alerta = """<script> alert("Por favor, primero inicie sesión."); window.location.href = "/login"; </script> """
        return alerta

#conexion bd con los productos
import os

@app.route('/producto', methods=['GET', 'POST'])
def formProducto():
    if request.method == 'POST':
        # Obtener datos del formulario
        idProducto = request.form['idProducto']
        nombreProducto = request.form['nombreProducto']
        categoria = request.form['categoria']
        cantidadProducto = request.form['unidades']
        precioProducto = request.form['precio']
        idVendedor = session.get('email')

        # Obtener la imagen del formulario
        if 'imagen' in request.files:
            imagen = request.files['imagen']
            if imagen.filename != '':
                filename = secure_filename(imagen.filename)
                ruta_imagen = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # Crear el directorio si no existe
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

                imagen.save(ruta_imagen)  # Guardar la imagen en el sistema de archivos
            else:
                ruta_imagen = None
        else:
            ruta_imagen = None

        # Guardar el producto en la base de datos junto con la ruta de la imagen
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO productos (idProducto, nombreProducto, categoria, cantidadProducto, precioProducto, idVendedor, imagen) VALUES (%s, %s, %s, %s, %s, %s, %s)", (idProducto, nombreProducto, categoria, cantidadProducto, precioProducto, idVendedor, ruta_imagen))
        mysql.connection.commit()
        cur.close()

        flash('Producto creado correctamente')
        return redirect(url_for('producto'))
    else:
        return render_template('formProducto.html')

    
@app.route("/Comprador")
def comprador():
    if 'logueado' in session and session['logueado']:
        if 'rol' in session:
            rol=session['rol']
            if rol=='Comprador':
                cur = mysql.connection.cursor()
                cur.execute('SELECT * FROM usuarios WHERE email = %s', (session['email'],))
                user = cur.fetchone()
                cur.close()
                return render_template('comprador/comprador.html', user=user)
            else:
                if rol=='Vendedor':
                    alerta = """<script> alert("No tienes permisos."); window.location.href = "/Vendedor"; </script>"""
                    return alerta
                elif rol=='Admin':
                    alerta = """<script> alert("No tienes permisos."); window.location.href = "/Administrador"; </script>"""
                    return alerta
    else:
        alerta = """<script> alert("Por favor, primero inicie sesión."); window.location.href = "/login"; </script> """
        return alerta

@app.route("/Tienda")
def compras():
    if 'logueado' in session and session['logueado']:
        if 'rol' in session:
            rol=session['rol']
            if rol=='Comprador':
                cur = mysql.connection.cursor() 
            
                cur.execute('SELECT * FROM productos')
                data2 = cur.fetchall()
                cur.execute('SELECT * FROM `productos` WHERE idProducto = 1')
                data = cur.fetchall()
                cur.execute('SELECT * FROM usuarios WHERE email = %s', (session['email'],))
                user = cur.fetchall()
                return render_template("comprador/compras.html", producto1=data, producto2=data2,user=user)
            else:
                if rol=='Vendedor':
                    alerta = """<script> alert("No tienes permisos."); window.location.href = "/Vendedor"; </script>"""
                    return alerta
                elif rol=='Admin':
                    alerta = """<script> alert("No tienes permisos."); window.location.href = "/Administrador"; </script>"""
                    return alerta 
    else:
        alerta = """<script> alert("Por favor, primero inicie sesión."); window.location.href = "/login"; </script> """
        return alerta
    
@app.route('/buscar_producto', methods=['GET','POST'])
def BuscarProducto():
    
    if 'logueado' in session and session['logueado']:
        if 'rol' in session:
            rol=session['rol']
            if rol=='Comprador':
                cur = mysql.connection.cursor() 
                if request.method == "POST":
                    search = request.form['buscar']
                    cur = mysql.connection.cursor() 
                    cur.execute("SELECT * FROM productos WHERE nombreproducto= '%s' ORDER BY nombreproducto DESC" % (search,))
                    busqueda = cur.fetchall()
                    cur.execute('SELECT * FROM usuarios WHERE email = %s', (session['email'],))
                    user = cur.fetchone()
                    return render_template("comprador/resultado_busqueda.html",miData=busqueda, busqueda=search, user=user)
            if rol=='Vendedor':
                alerta = """<script> alert("No tienes permisos."); window.location.href = "/Vendedor"; </script>"""
                return alerta
            elif rol=='Admin':
                alerta = """<script> alert("No tienes permisos."); window.location.href = "/Administrador"; </script>"""
                return alerta 
            else:
                alerta = """<script> alert("Por favor, primero inicie sesión."); window.location.href = "/login"; </script> """
                return alerta
        
    

@app.route('/agregar_al_carrito', methods=['GET','POST'])
def agregar_al_carrito():
        idP=request.form['idP']
        nombre_producto = request.form['nombre_producto']
        precio_producto = request.form['precio']
        cantidad = int(request.form['cantidad'])
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO carrito (idP,nombre_producto, precio_producto, cantidad) VALUES (%s, %s, %s,%s)", (idP,nombre_producto, precio_producto, cantidad))
        mysql.connection.commit()
        alerta = """<script> alert("Producto agregado al carrito"); window.location.href = "/Tienda"; </script>"""
        return alerta
    
@app.route("/Frutas")
def categorias():
    if 'logueado' in session and session['logueado']:
        if 'rol' in session:
            rol=session['rol']
            if rol=='Comprador':
                cur = mysql.connection.cursor() 
                cur.execute("SELECT * FROM productos WHERE categoria = 'frutas'")
                categoria1 = cur.fetchall()
                cur.execute('SELECT * FROM usuarios WHERE email = %s', (session['email'],))
                user = cur.fetchone()
                return render_template("comprador/compras.html",producto1=categoria1,user=user)
            else:
                if rol=='Vendedor':
                    alerta = """<script> alert("No tienes permisos."); window.location.href = "/Vendedor"; </script>"""
                    return alerta
                elif rol=='Admin':
                    alerta = """<script> alert("No tienes permisos."); window.location.href = "/Administrador"; </script>"""
                    return alerta 
    else:
        alerta = """<script> alert("Por favor, primero inicie sesión."); window.location.href = "/login"; </script> """
        return alerta
    
@app.route("/Legumbres")
def categorias3():
    if 'logueado' in session and session['logueado']:
        if 'rol' in session:
            rol=session['rol']
            if rol=='Comprador':
                cur = mysql.connection.cursor() 
                cur.execute("SELECT * FROM productos WHERE categoria = 'legumbres'")
                data1 = cur.fetchall()
                cur.execute('SELECT * FROM usuarios WHERE email = %s', (session['email'],))
                user = cur.fetchone()
                return render_template("comprador/compras.html",producto1=data1,user=user)
            else:
                if rol=='Vendedor':
                    alerta = """<script> alert("No tienes permisos."); window.location.href = "/Vendedor"; </script>"""
                    return alerta
                elif rol=='Admin':
                    alerta = """<script> alert("No tienes permisos."); window.location.href = "/Administrador"; </script>"""
                    return alerta 
    else:
        alerta = """<script> alert("Por favor, primero inicie sesión."); window.location.href = "/login"; </script> """
        return alerta

@app.route("/Vegetales")
def categorias1():
    if 'logueado' in session and session['logueado']:
        if 'rol' in session:
            rol=session['rol']
            if rol=='Comprador':
                cur = mysql.connection.cursor() 
                cur.execute("SELECT * FROM productos WHERE categoria = 'vegetales'")
                data1 = cur.fetchall()
                cur.execute("SELECT * FROM productos WHERE categoria = 'hortalizas'")
                data2 = cur.fetchall()
                cur.execute('SELECT * FROM usuarios WHERE email = %s', (session['email'],))
                user = cur.fetchone()
                return render_template("comprador/compras.html",producto1=data1,producto2=data2,user=user)
            else:
                if rol=='Vendedor':
                    alerta = """<script> alert("No tienes permisos."); window.location.href = "/Vendedor"; </script>"""
                    return alerta
                elif rol=='Admin':
                    alerta = """<script> alert("No tienes permisos."); window.location.href = "/Administrador"; </script>"""
                    return alerta 
    else:
        alerta = """<script> alert("Por favor, primero inicie sesión."); window.location.href = "/login"; </script> """
        return alerta


@app.route('/carrito')
def ver_carrito():
    if 'logueado' in session and session['logueado']:
        if 'rol' in session:
            rol=session['rol']
            if rol=='Comprador':
                cursor = mysql.connection.cursor()
                cursor.execute("SELECT * FROM carrito")
                productos_carrito = cursor.fetchall()
                cursor.execute('SELECT * FROM usuarios WHERE email = %s', (session['email'],))
                user = cursor.fetchone()
                total = sum([producto[2] * producto[3] for producto in productos_carrito])  # Calcula el total
                return render_template('comprador/carrito.html', productos_carrito=productos_carrito, total=total,user=user)
            else:
                if rol=='Vendedor':
                    alerta = """<script> alert("No tienes permisos."); window.location.href = "/Vendedor"; </script>"""
                    return alerta
                elif rol=='Admin':
                    alerta = """<script> alert("No tienes permisos."); window.location.href = "/Administrador"; </script>"""
                    return alerta 
    else:
        alerta = """<script> alert("Por favor, primero inicie sesión."); window.location.href = "/login"; </script> """
        return alerta

@app.route('/pagar', methods=['POST'])
def pagar():
    if 'logueado' in session and session['logueado']:
        if 'rol' in session:
            rol=session['rol']
            if rol=='Comprador':  
                cursor = mysql.connection.cursor()
                cursor.execute("SELECT SUM(precio_producto * cantidad) FROM carrito")
                total = cursor.fetchone()[0]
                user = session.get('email')
                cursor.execute("INSERT INTO transacciones (fechaVenta, total, idComprador) VALUES (%s, %s, %s)",
                                (datetime.now(), total, user))
                mysql.connection.commit()
                cursor.execute("DELETE FROM carrito")
                mysql.connection.commit()
                alerta = """<script> alert("Pago realizaado correctamente"); window.location.href = "/Tienda"; </script>"""
                return alerta
            else:
                if rol=='Vendedor':
                    alerta = """<script> alert("No tienes permisos."); window.location.href = "/Vendedor"; </script>"""
                    return alerta
                elif rol=='Admin':
                    alerta = """<script> alert("No tienes permisos."); window.location.href = "/Administrador"; </script>"""
                    return alerta 
    else:
        alerta = """<script> alert("Por favor, primero inicie sesión."); window.location.href = "/login"; </script> """
        return alerta

@app.route('/MisCompras')
def compra():
    if 'logueado' in session and session['logueado']:
        if 'rol' in session:
            rol=session['rol']
            if rol=='Admin':
                cur = mysql.connection.cursor()
                cur.execute('SELECT * FROM transacciones')
                data = cur.fetchall()
                cur.execute('SELECT * FROM usuarios WHERE email = %s', (session['email'],))
                user = cur.fetchone()
                return render_template("administrador/productos.html", produ=data,user=user)
            else:
                if rol=='Vendedor':
                    alerta = """<script> alert("No tienes permisos."); window.location.href = "/Vendedor"; </script>"""
                    return alerta
                elif rol=='Comprador':
                    Usuario = session['email']
                    cur = mysql.connection.cursor()
                    cur.execute('SELECT * FROM transacciones WHERE idComprador = %s', (Usuario,))
                    data = cur.fetchall()
                    cur.execute('SELECT * FROM usuarios WHERE email = %s', (session['email'],))
                    user = cur.fetchone()
                    return render_template('/comprador/crud_compras.html', compras=data,user=user)
    else:
        alerta = """<script> alert("Por favor, primero inicie sesión."); window.location.href = "/login"; </script> """
        return alerta

if __name__ == '__main__':
    app.run(debug=True)