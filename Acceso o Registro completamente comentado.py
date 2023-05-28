#Importe de librerias
import mysql.connector
from hashlib import sha256
from getpass import getpass
import os
import time
from datetime import datetime

db = None  # Variable para almacenar la conexión a la base de datos (inicialmente se establece como None)
cursor = None  # Variable para almacenar el cursor de la base de datos (inicialmente se establece como None)
sesion = None  # Variable para almacenar la sesión (inicialmente se establece como None)
opc_selected = None  # Variable para almacenar la opción seleccionada (inicialmente se establece como None)
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Variable para almacenar la fecha y hora actual en formato de cadena ("YYYY-MM-DD HH:MM:SS")

#Funcion para cambiar el color de la salida de texto
class bcolors:
    OK = '\033[92m' #VERDE
    WARNING = '\033[93m' #AMARILLO
    FAIL = '\033[91m' #ROJO
    RESET = '\033[0m' #REINICIAR COLOR

#Funcion usada para impiar la terminal
def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')#código se utiliza para limpiar la pantalla de la consola, 

#Funcion para conectar a la bd
def inicializar_database():
    try:
        global db, cursor
        # Establecer la conexión con la base de datos
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="db_proyecto"
        )
        # Crear un cursor para ejecutar consultas en la base de datos
        cursor = db.cursor()

        # Verificar si la conexión fue exitosa
        if db.is_connected():
            print("CONEXION EXITOSA")
            print("INICANDO...")
            # Pausa de 1.5 segundos antes de continuar
            time.sleep(1.5)
            # Llamar a la función "limpiar_pantalla()" para limpiar la pantalla (suponemos que está definida en otro lugar)
            limpiar_pantalla()
    except Exception as ex:
        # Si ocurre una excepción, mostrar el mensaje de error
        print(ex)
        print("POR FAVOR CONTACTE CON UN ADMINISTRADOR")
        # Pausa de 4 segundos antes de continuar
        time.sleep(4)

#Corta conexion
def cerrar_conex_db():
    if cursor:
        cursor.close()#Cierra cursor
    if db:
        db.close()#Cierra la bd

#Funcion que recopila el usuario y contraseña registrandolos en la bd
def register():
    while True:
        limpiar_pantalla()   # Llama a la función "limpiar_pantalla()" para limpiar la pantalla de la consola
        print("---------------------------------------")
        print("|               Registro              |")
        print("---------------------------------------")
        username = input("Nombre de usuario: ")  # Solicita al usuario ingresar un nombre de usuario
        password = input("Contraseña: ")  # Solicita al usuario ingresar una contraseña
        password_verify = input("Vuelve a introducir la contraseña: ")  # Solicita al usuario ingresar nuevamente la contraseña

        if password == password_verify:  # Verifica si las contraseñas coinciden
            print("Las contraseñas coinciden")
            time.sleep(1)  # Espera 1 segundo
            break  # Sale del bucle interno
        else:
            print("Las contraseñas no coinciden, vuelve a intentarlo")
            time.sleep(1)  # Espera 1 segundo
            limpiar_pantalla() # Llama a la función "limpiar_pantalla()" para limpiar la pantalla de la consola

        # Consulta si el nombre de usuario ya existe en la base de datos
        sql = "SELECT nombre_usuario FROM usuarios WHERE nombre_usuario = %s"
        cursor.execute(sql, (username,))
        result = cursor.fetchone()
    
        if result is None:  # Si el resultado de la consulta es None, el nombre de usuario no existe
            print("Registrando...")
            time.sleep(3)  # Espera 3 segundos
            rol = 'user'
            ## Se cifra la contraseña
            salt = "s3cr3t5alt"
            hashed_password = sha256((password + salt).encode()).hexdigest()
            ## La contraseña se carga en la base de datos
            sql = "INSERT INTO usuarios (nombre_usuario, contraseña, rol) VALUES (%s, %s, %s)"
            values = (username, hashed_password, rol)
            cursor.execute(sql, values)
            db.commit()
            # Indica que el registro fue exitoso
            limpiar_pantalla()  # Llama a la función "limpiar_pantalla()" para limpiar la pantalla de la consola
            print("Usuario registrado correctamente.")
            time.sleep(1)  # Espera 1 segundo
            # Registrar en el historial
            registrar_historial(f"Registro de usuario", username)
            break
        else:
            print("El usuario ya existe, vuelve a intentarlo")
            time.sleep(1)  # Espera 1 segundo

#Funcion que compara el usuario y contraseña con las ingresadas a la bd para iniciar sesion
def login():
    # Se definen las variables globales role, username y password
    global role, username, password
    limpiar_pantalla()  # Llama a la función "limpiar_pantalla()" para limpiar la pantalla de la consola
    print("---------------------------------------")
    print("|                Acceso                |")  # Imprime el encabezado de inicio de sesión
    print("---------------------------------------")
    username = input("Nombre de usuario: ")  # Solicita al usuario que ingrese su nombre de usuario
    password = getpass("Contraseña: ")  # Solicita al usuario que ingrese su contraseña de manera segura (sin mostrarla en pantalla)
    sql = "SELECT contraseña, rol FROM usuarios WHERE nombre_usuario = %s"  # Consulta SQL para obtener la contraseña y el rol asociados al nombre de usuario ingresado
    cursor.execute(sql, (username,))  # Ejecuta la consulta SQL con el nombre de usuario proporcionado
    result = cursor.fetchone()  # Obtiene el resultado de la consulta
    if result is None:  # Si no se encontró ningún resultado en la consulta
        print("Nombre de usuario incorrecto. Vuelve a intentarlo")  # Imprime un mensaje de error
        time.sleep(1)  # Espera 1 segundo antes de continuar
    else:
        hashed_password = result[0]  # Obtiene la contraseña almacenada en el resultado de la consulta
        role = result[1]  # Obtiene el rol almacenado en el resultado de la consulta
        salt = "s3cr3t5alt"  # Define una sal (salt) para fortalecer la contraseña
        entered_password = sha256((password + salt).encode()).hexdigest()  # Aplica el hash a la contraseña ingresada por el usuario
        if hashed_password == entered_password:  # Si la contraseña ingresada coincide con la almacenada en la base de datos
            limpiar_pantalla()  # Llama a la función "limpiar_pantalla()" para limpiar la pantalla de la consola
            if role == "admin":  # Si el rol es "admin"
                print("¡Bienvenido administrador!")  # Imprime un mensaje de bienvenida para el administrador
                menu_home()  # Llama a la función "menu_home()" para mostrar el menú principal 
            else:
                print(f"Bienvenido @{username} inicio de sesión exitoso")  # Imprime un mensaje de bienvenida para el usuario con su nombre de usuario
                menu_home()  # Llama a la función "menu_home()" para mostrar el menú principal
            registrar_historial(f"Inicio de sesión", username)  # Registra el inicio de sesión en el historial
            return True  # Retorna True para indicar un inicio de sesión exitoso
        else:
            print("Contraseña incorrecta.")  # Imprime un mensaje de error de contraseña incorrecta
            time.sleep(1.5)  # Espera 1.5 segundos antes de continuar
    return False  # Retorna False para indicar un inicio de sesión fallido


#Codigo para cambio de contraseña
def change_password():
    limpiar_pantalla()  # Llama a la función "limpiar_pantalla()" para limpiar la pantalla de la consola
    print("---------------------------------------")
    print("|         Cambiar contraseña          |")
    print("---------------------------------------")
    username = input("Nombre de usuario: ") # Solicita al usuario que ingrese el nombre de usuario.
    current_password = getpass("Contraseña actual: ") # Solicita al usuario que ingrese la contraseña actual sin mostrarla en pantalla.
    new_password = getpass("Nueva contraseña: ") # Solicita al usuario que ingrese la nueva contraseña sin mostrarla en pantalla.

    # Consulta la base de datos para obtener la contraseña almacenada asociada al nombre de usuario ingresado.
    sql = "SELECT contraseña FROM usuarios WHERE nombre_usuario = %s"
    cursor.execute(sql, (username,))
    result = cursor.fetchone()

    if result is None:
        print("Nombre de usuario incorrecto.") # Si no se encuentra un resultado, el nombre de usuario ingresado es incorrecto.
    else:
        hashed_password = result[0] # La contraseña almacenada en la base de datos.
        salt = "s3cr3t5alt" # Una sal (salt) que se agrega a la contraseña antes de generar su hash.
        entered_password = sha256((current_password + salt).encode()).hexdigest() # Genera el hash de la contraseña actual ingresada por el usuario.

        if hashed_password == entered_password:
            # Si el hash de la contraseña ingresada coincide con el hash almacenado en la base de datos, procede a actualizar la contraseña.
            new_hashed_password = sha256((new_password + salt).encode()).hexdigest() # Genera el hash de la nueva contraseña.
            update_sql = "UPDATE usuarios SET contraseña = %s WHERE nombre_usuario = %s"
            cursor.execute(update_sql, (new_hashed_password, username))
            db.commit()

            limpiar_pantalla() # Llama a la función "limpiar_pantalla()" para limpiar la pantalla de la consola
            print("Contraseña actualizada correctamente.")

            # Registrar en el historial
            registrar_historial(f"Cambio de contraseña", username) # Registra el evento de cambio de contraseña en el historial.
        else:
            limpiar_pantalla() # Llama a la función "limpiar_pantalla()" para limpiar la pantalla de la consola
            print("Contraseña incorrecta.") # Si los hashes no coinciden, la contraseña actual ingresada es incorrecta.

#Codigo por si no se introduce un cacter valido
def opcion_incorrecta():
    print("Error: Opción Incorrecta")  # Imprime un mensaje de error indicando que la opción seleccionada es incorrecta.
    print("La opción seleccionada no es un número o no es una opción disponible")  # Imprime un mensaje que indica que la opción no es un número válido o no está disponible.
    print("VUELVE A INTENTARLO")  # Imprime un mensaje instando al usuario a intentarlo nuevamente.
#Menu Principal 
def menu_principal():
    limpiar_pantalla()   # Llama a la función "limpiar_pantalla()" para limpiar la pantalla de la consola
    print("---------------------------------------")
    print("|            MENU PRINCIPAL           |")
    print("|-------------------------------------|")
    print("|  1.- Registro                       |")  # Opción 1: Registro
    print("|  2.- Acceso                         |")  # Opción 2: Inicio de sesión
    print("|  3.- Cambiar contraseña             |")  # Opción 3: Cambiar contraseña
    print("|  4.- Salir                          |")  # Opción 4: Salir
    print("|-------------------------------------|")
    print("|Consult Date:", timestamp, "   |")  # Fecha de consulta 
    print("---------------------------------------")

#Funcion para el proceso de seleccion en los menus
def seleccion():
    global opc_selected  # Declarando la variable opc_selected como global
    while True:  # Bucle infinito
        try:
            opc_selected = int(input("Escribe la opción a seleccionar: "))  # Solicitando al usuario que ingrese la opción seleccionada
            return opc_selected  # Devolviendo el valor de la opción seleccionada
        except ValueError:  # Capturando una excepción si el usuario ingresa un valor no válido
            opcion_incorrecta()  # Llamando a una función llamada opcion_incorrecta 
            time.sleep(0.5)  # Haciendo una pausa de 0.5 segundos
            limpiar_pantalla()  # Llama a la función "limpiar_pantalla()" para limpiar la pantalla de la consola

#Funcion que muestra el historial guardado en la bd
def mostrar_historial():
    sql = "SELECT * FROM historial WHERE usuario = %s ORDER BY fecha_hora DESC"  # Consulta SQL para obtener el historial del usuario específico
    cursor.execute(sql, (username,))  # Ejecutar la consulta SQL con el valor del nombre de usuario proporcionado
    result = cursor.fetchall()  # Obtener todos los resultados de la consulta

    if result:  # Si hay resultados
        limpiar_pantalla()  # Llamar a la función para limpiar la pantalla
        print("--------------------------------------------")
        print("|                 Historial                |")  # Imprimir encabezado del historial
        print("--------------------------------------------")
        for row in result:  # Iterar sobre cada fila de resultados
            print("ID de referencia:", row[0])  # Imprimir el ID de referencia de la acción
            print(bcolors.OK + "Acción:", row[1] + bcolors.RESET)  # Imprimir la acción resaltada en color verde
            print("Fecha y hora:", row[2])  # Imprimir la fecha y hora de la acción
            print("--------------------------------------------")

    else:
        print("No hay registros en el historial.")  # Imprimir mensaje si no hay registros en el historial


def borrar_historial():
    limpiar_pantalla()  # Llamar a la función para limpiar la pantalla
    confirmacion = input(bcolors.WARNING + "¿Estás seguro de que quieres borrar el historial? (s/n): " + bcolors.RESET)  # Solicitar confirmación para borrar el historial
    if confirmacion.lower() == 's':  # Si la confirmación es 's'
        sql = "TRUNCATE TABLE historial"  # Consulta SQL para borrar todos los registros de la tabla 'historial'
        cursor.execute(sql)  # Ejecutar la consulta SQL
        db.commit()  # Confirmar los cambios en la base de datos
        time.sleep(1)
        print("Historial borrado correctamente.")  # Imprimir mensaje de confirmación
    else:
        print("Operación cancelada.")  # Imprimir mensaje si la operación es cancelada
        time.sleep(1)


def mostrar_usuarios():
    limpiar_pantalla()  # Llamar a la función para limpiar la pantalla
    sql = "SELECT * FROM usuarios ORDER BY fecha_hora ASC"  # Consulta SQL para obtener todos los usuarios ordenados por fecha y hora
    cursor.execute(sql)  # Ejecutar la consulta SQL
    result = cursor.fetchall()  # Obtener todos los resultados de la consulta

    if result:  # Si hay resultados
        print("------------------------------------------------")
        print("|            Uuarios registrados               |")  # Imprimir encabezado de los usuarios registrados
        print("------------------------------------------------")
        limpiar_pantalla()  # Llamar a la función para limpiar la pantalla
        for row in result:  # Iterar sobre cada fila de resultados
            print("ID de referencia:", row[0])  # Imprimir el ID de referencia del usuario
            print(bcolors.OK + "Acción:", row[1] + bcolors.RESET)  # Imprimir la acción resaltada en color verde
            print("Fecha y hora:", row[2])  # Imprimir la fecha y hora de la acción
            print(bcolors.OK + "Usuario:", row[3] + bcolors.RESET)  # Imprimir el nombre de usuario resaltado en color verde
            print("---------------------------------------")
    else:
        print("No hay registros en el historial de usuarios.")  # Imprimir mensaje si no hay registros de usuarios


def eliminar_usuario():
    limpiar_pantalla()  # Llamar a la función para limpiar la pantalla
    user = input(bcolors.WARNING + "Ingresa el nombre de usuario que deseas eliminar del sistema: " + bcolors.RESET)  # Solicitar el nombre de usuario a eliminar
    verify = getpass(bcolors.WARNING + "Ingresa tu contraseña administrador: " + bcolors.RESET)  # Solicitar la contraseña de administrador

    if verify == password:  # Si la contraseña coincide con la contraseña de administrador
        print(bcolors.OK + "\nLas contraseñas coinciden\n" + bcolors.RESET)  # Imprimir mensaje de confirmación
        time.sleep(0.5)
        confirmacion = input(bcolors.FAIL + "¿Estás seguro de que quieres eliminar al usuario? (s/n): " + bcolors.RESET)  # Solicitar confirmación para eliminar al usuario
        if confirmacion.lower() == 's':  # Si la confirmación es 's'
            time.sleep(1)
            print(bcolors.WARNING + "Eliminando usuario..." + bcolors.RESET)
            sql = "DELETE FROM usuarios WHERE nombre_usuario = %s;"  # Consulta SQL para eliminar al usuario de la tabla 'usuarios'
            cursor.execute(sql, (user,))  # Ejecutar la consulta SQL con el valor del nombre de usuario proporcionado
            db.commit()  # Confirmar los cambios en la base de datos
            time.sleep(2)
            print(bcolors.OK + "Usuario eliminado exitosamente" + bcolors.RESET)  # Imprimir mensaje de confirmación
            # Registrar en el historial
            registrar_historial(f"Eliminación de usuario", user)  # Llamar a la función para registrar la acción en el historial
        else: 
            print("Operación cancelada.")  # Imprimir mensaje si la operación es cancelada
            time.sleep(1)
    else:
        print("La contraseña no es correcta.")  # Imprimir mensaje si la contraseña no coincide
        print("Cancelando operación...")
        time.sleep(1)


def mostrar_historial_admin():
    sql = "SELECT * FROM historial ORDER BY fecha_hora ASC"  # Consulta SQL para obtener todo el historial ordenado por fecha y hora
    cursor.execute(sql)  # Ejecutar la consulta SQL
    result = cursor.fetchall()  # Obtener todos los resultados de la consulta

    if result:  # Si hay resultados
        limpiar_pantalla()  # Llamar a la función para limpiar la pantalla
        print("---------------------------------------")
        print("|         Historial de Usuarios       |")  # Imprimir encabezado del historial de usuarios
        print("---------------------------------------")
        for row in result:  # Iterar sobre cada fila de resultados
            print("ID de referencia:", row[0])  # Imprimir el ID de referencia de la acción
            print(bcolors.OK + "Acción:", row[1] + bcolors.RESET)  # Imprimir la acción resaltada en color verde
            print("Fecha y hora:", row[2])  # Imprimir la fecha y hora de la acción
            print(bcolors.OK + "Usuario:", row[3] + bcolors.RESET)  # Imprimir el nombre de usuario resaltado en color verde
            print("---------------------------------------")
    else:
        print("No hay registros en el historial de usuarios.")  # Imprimir mensaje si no hay registros en el historial de usuarios


def menu_admin():
    while True:
        print("""----------------------------------
            |         MENÚ ADMINISTRADOR          |
            |-------------------------------------|
            | 1.- Mostrar Historial               |
            | 2.- Borrar Historial                |
            | 3.- Eliminar usuario                |
            | 4.- Salir                           |
            ---------------------------------------""")
        seleccion()  # Solicitar al usuario que seleccione una opción del menú

        if opc_selected == 1:
            mostrar_historial_admin()  # Llamar a la función para mostrar el historial de usuarios como administrador
            input("Presiona Enter para continuar...")
            limpiar_pantalla()
        elif opc_selected == 2:
            borrar_historial()  # Llamar a la función para borrar el historial
            input("Presiona Enter para continuar...")
            limpiar_pantalla()
        elif opc_selected == 3:
            eliminar_usuario()  # Llamar a la función para eliminar un usuario
            input("Presiona Enter para continuar...")
            limpiar_pantalla()
        elif opc_selected == 4:
            break
        else:
            opcion_incorrecta()  # Llamar a la función si se selecciona una opción incorrecta


def menu_home():
    global sesion
    if sesion:
        while True:
            print("------------------------------")
            print("|     ¿Qué deseas hacer?     |")
            print("|----------------------------|")
            print("|   5.- Cambiar contraseña   |")
            if role == 'admin':
                print("|   6.- Menu Administrador   |")
            else:
                print("|   6.- Historial            |")
            print("|   7.- Salir                |")
            print("------------------------------")
            seleccion()  # Solicitar al usuario que seleccione una opción del menú

            if opc_selected == 5:
                change_password()  # Llamar a la función para cambiar la contraseña
                input("Presiona Enter para continuar...")
                limpiar_pantalla()
            elif opc_selected == 6:
                if role == 'admin':
                    limpiar_pantalla()
                    menu_admin()  # Llamar al menú del administrador
                    input("Presiona Enter para continuar...")
                    limpiar_pantalla()
                else:
                    limpiar_pantalla()
                    mostrar_historial()  # Llamar a la función para mostrar el historial del usuario
                    input("Presiona Enter para continuar...")
                    limpiar_pantalla()
            elif opc_selected == 7:
                sesion = False
                break
            else:
                opcion_incorrecta()  # Llamar a la función si se selecciona una opción incorrecta


def registrar_historial(accion, username):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Obtener la marca de tiempo actual
    sql = "INSERT INTO historial (accion, fecha_hora, usuario) VALUES (%s, %s, %s)"  # Consulta SQL para registrar la acción en el historial
    values = (accion, timestamp, username)  # Valores a insertar en la consulta SQL
    cursor.execute(sql, values)  # Ejecutar la consulta SQL con los valores proporcionados
    db.commit()  # Confirmar los cambios en la base de datos


try:
    inicializar_database()  # Llamar a la función para inicializar la base de datos
    limpiar_pantalla()  # Llamar a la función para limpiar la pantalla
    print("Sistema de Registro de Usuarios")
    print("---------------------------------")

    while True:
        print("---------------------------------------")
        print("|              MENÚ INICIO             |")
        print("|--------------------------------------|")
        print("| 1.- Iniciar sesión                   |")
        print("| 2.- Registrar usuario                |")
        print("| 3.- Salir                            |")
        print("----------------------------------------")
        seleccion()  # Solicitar al usuario que seleccione una opción del menú

        if opc_selected == 1:
            login()  # Llamar a la función para iniciar sesión
            if sesion:
                menu_home()  # Llamar al menú principal si la sesión se ha iniciado correctamente
                break
            else:
                input("Presiona Enter para continuar...")
                limpiar_pantalla()
        elif opc_selected == 2:
            register()  # Llamar a la función para registrar un usuario
            input("Presiona Enter para continuar...")
            limpiar_pantalla()
        elif opc_selected == 3:
            break
        else:
            opcion_incorrecta()  # Llamar a la función si se selecciona una opción incorrecta

    cursor.close()  # Cerrar el cursor
    db.close()  # Cerrar la conexión a la base de datos
    print("¡Hasta luego!")

except Exception as e:
    print("Se produjo un error:", e)
    cursor.close()  # Cerrar el cursor
    db.close()  # Cerrar la conexión a la base de datos
