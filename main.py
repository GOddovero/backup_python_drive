import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog ,BooleanVar, Checkbutton
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from datetime import datetime
import locale
import shutil
import os


"""
Este script se encarga de crear un backup de la carpeta "archivos" y subirla a Google Drive.
El nombre del archivo se generará según el día de la semana:
    - Si es sábado, el nombre del archivo será "backup_semanal_<fecha_actual>.zip"
    - Si no es sábado, el nombre del archivo será "backup_diario.zip"

El script verificará si el archivo ya existe en Google Drive y lo eliminará si es necesario.
Finalmente, se creará y subirá el archivo a Google Drive.
"""
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')  # Cambiamos el lenguaje a Español.
ruta_configuracion = "./config/config_carpetas.txt"
configuraciones = {}  # Diccionario para almacenar las configuraciones

# Verificar si el archivo existe antes de intentar abrirlo
def leer_configuraciones():
    """Leer las configuraciones del archivo."""
    if not os.path.exists(ruta_configuracion):
        mensaje_error(f"No se encontró el archivo de configuración en la ruta: {ruta_configuracion}")
        return
    
    try:
        with open(ruta_configuracion, 'r') as archivo:
            for linea in archivo:
                if '=' in linea and linea.strip():
                    clave, valor = linea.strip().split('=', 1)
                    configuraciones[clave.strip()] = valor.strip()

        global CARPETA_LOCAL, CARPETA_DRIVE, AUTOMATICO
        CARPETA_LOCAL = configuraciones.get('CARPETA_LOCAL', './archivos')
        CARPETA_DRIVE = configuraciones.get('CARPETA_DRIVE', '1V9wcEfJ-COdDKlpEUghwKRAVhL3FyCaC')
        AUTOMATICO = configuraciones.get('AUTOMATICO', 'False') == 'True'
        mensaje_info(f"Configuraciones cargadas:\nCarpeta Local: {CARPETA_LOCAL}\nCarpeta Drive: {CARPETA_DRIVE}\nAutomático: {AUTOMATICO}")
    except Exception as e:
        mensaje_error(f"Error al leer el archivo de configuración: {e}")

def guardar_configuraciones():
    """Guardar las configuraciones actuales en el archivo."""
    try:
        with open(ruta_configuracion, 'w') as archivo:
            for clave, valor in configuraciones.items():
                archivo.write(f"{clave}={valor}\n")
        mensaje_info("Configuraciones guardadas correctamente.")
    except Exception as e:
        mensaje_error(f"Error al guardar las configuraciones: {e}")
def modificar_configuracion():
    """Permitir al usuario modificar las configuraciones del backup y actualizarlas."""
    try:
        # Seleccionar una nueva carpeta
        nueva_carpeta = filedialog.askdirectory(title="Selecciona la nueva carpeta para el backup local")
        if nueva_carpeta:
            configuraciones['CARPETA_LOCAL'] = nueva_carpeta
        
        # Ingresar un nuevo ID de la CARPETA_DRIVE
        nuevo_id_drive = simpledialog.askstring("Modificar ID de la Carpeta en Drive", "Ingresa el nuevo ID de la carpeta de Google Drive:", initialvalue=configuraciones.get('CARPETA_DRIVE', ''))
        if nuevo_id_drive:
            configuraciones['CARPETA_DRIVE'] = nuevo_id_drive
        
        # Modificar el valor de AUTOMATICO
        es_automatico = BooleanVar()
        es_automatico.set(configuraciones.get('AUTOMATICO', 'False') == 'True')
        ventana_automatica = tk.Toplevel(ventana)  # Crear una ventana secundaria
        ventana_automatica.title("Configurar Backup Automático")
        
        check_automatico = tk.Checkbutton(ventana_automatica, text="Backup Automático", variable=es_automatico, command=lambda: actualizar_automatico(es_automatico.get()))
        check_automatico.pack(pady=10)
        ventana_automatica.mainloop()
        
        # Guardar configuraciones actualizadas
        guardar_configuraciones()
        leer_configuraciones()  # Volver a leer las configuraciones después de modificar
    except Exception as e:
        mensaje_error(f"Error al modificar la configuración: {e}")

def actualizar_automatico(valor):
    """Actualizar la configuración AUTOMATICO y guardar el archivo."""
    configuraciones['AUTOMATICO'] = 'True' if valor else 'False'
    guardar_configuraciones()

def realizar_backup():
    """Realizar el backup y subirlo a Google Drive."""
    leer_configuraciones()

    # Autenticación y creación del cliente de Google Drive
    try:
        gauth = GoogleAuth()
        gauth.LoadClientConfigFile("./config/credenciales.json")
        gauth.LocalWebserverAuth()
        drive = GoogleDrive(gauth)

        fecha_actual = datetime.now()
        nombre_archivo_backup = f"backup_semanal_{fecha_actual.strftime('%Y-%m-%d')}.zip" if fecha_actual.strftime('%A') == 'sábado' else "backup_diario.zip"
        zip_path = f"./{nombre_archivo_backup}"
        shutil.make_archive(nombre_archivo_backup.replace('.zip', ''), 'zip', CARPETA_LOCAL)

        # Verificar si el archivo ya existe en Google Drive y eliminarlo si es necesario
        file_list = drive.ListFile({'q': f"'{CARPETA_DRIVE}' in parents and trashed=false"}).GetList()
        for file in file_list:
            if file['title'] == nombre_archivo_backup:
                file.Delete()

        # Crear y subir el archivo a Google Drive
        archivo = drive.CreateFile({'title': nombre_archivo_backup, 'parents': [{'id': CARPETA_DRIVE}]})
        archivo.SetContentFile(zip_path)
        archivo.Upload()
        mensaje_info(f"Archivo de backup '{nombre_archivo_backup}' subido con éxito a Google Drive.")
    except Exception as e:
        mensaje_error(f"Error al realizar el backup: {e}")
        print(e)

def mensaje_info(mensaje):
    """Mostrar mensaje informativo."""
    messagebox.showinfo("Información", mensaje)

def mensaje_error(mensaje):
    """Mostrar mensaje de error."""
    messagebox.showerror("Error", mensaje)

def centrar_ventana(ventana, ancho, alto):
    """Centrar la ventana en la pantalla."""
    x_ventana = ventana.winfo_screenwidth() // 2 - ancho // 2
    y_ventana = ventana.winfo_screenheight() // 2 - alto // 2
    ventana.geometry(f'{ancho}x{alto}+{x_ventana}+{y_ventana}')

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Backup y Configuración")
ventana.configure(bg="#f0f0f0")  # Fondo gris claro
centrar_ventana(ventana, 400, 250)  # Centrar la ventana

# Marco para los botones
frame_botones = tk.Frame(ventana, bg="#f0f0f0")
frame_botones.pack(pady=20)

# Estilos de los botones
estilo_boton = {'font': ('Arial', 12), 'bg': '#4CAF50', 'fg': 'white', 'padx': 10, 'pady': 5}

# Botón para realizar backup
btn_backup = tk.Button(frame_botones, text="Realizar Backup", command=realizar_backup, **estilo_boton)
btn_backup.grid(row=0, column=0, padx=10, pady=10)

# Botón para modificar configuración
btn_modificar = tk.Button(frame_botones, text="Modificar Configuración", command=modificar_configuracion, **estilo_boton)
btn_modificar.grid(row=0, column=1, padx=10, pady=10)

# Etiqueta para mostrar mensajes informativos
lbl_mensaje = tk.Label(ventana, text="Selecciona una acción", font=('Arial', 10), bg="#f0f0f0", fg="#333")
lbl_mensaje.pack(pady=10)

ventana.mainloop()