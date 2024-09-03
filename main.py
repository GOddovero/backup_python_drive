from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from datetime import datetime
import locale
import shutil

"""
Este script se encarga de crear un backup de la carpeta "archivos" y subirla a Google Drive.
El nombre del archivo se generará según el día de la semana:
    - Si es sábado, el nombre del archivo será "backup_semanal_<fecha_actual>.zip"
    - Si no es sábado, el nombre del archivo será "backup_diario.zip"

El script verificará si el archivo ya existe en Google Drive y lo eliminará si es necesario.
Finalmente, se creará y subirá el archivo a Google Drive.
"""
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')  # Cambiamos el lenguaje a Español.

# Autenticación y creación del cliente de Google Drive.
gauth = GoogleAuth()

# Cambia esto a LoadClientConfigFile para cargar la configuración de cliente
gauth.LoadClientConfigFile("credenciales.json")  # Cambia a LoadClientConfigFile
gauth.LocalWebserverAuth()  # Abre una ventana en el navegador para autenticar.
drive = GoogleDrive(gauth)

CARPETA_LOCAL = "./archivos"
CARPETA_DRIVE = "1V9wcEfJ-COdDKlpEUghwKRAVhL3FyCaC" 

fecha_actual = datetime.now()

# Generar el nombre del archivo según el día de la semana
nombre_archivo_backup = ""
if fecha_actual.strftime('%A') == 'sábado':
    nombre_archivo_backup = f"backup_semanal_{fecha_actual.strftime('%Y-%m-%d')}.zip"
else:
    nombre_archivo_backup = "backup_diario.zip"

# Crear un archivo ZIP del directorio
zip_path = f"./{nombre_archivo_backup}"
shutil.make_archive(nombre_archivo_backup.replace('.zip', ''), 'zip', CARPETA_LOCAL)

# Verificar si el archivo ya existe en Google Drive y eliminarlo si es necesario
file_list = drive.ListFile({'q': f"'{CARPETA_DRIVE}' in parents and trashed=false"}).GetList()

for file in file_list:
    if file['title'] == nombre_archivo_backup:
        file.Delete()  # Borrar el archivo anterior para subir el nuevo

# Crear y subir el archivo a Google Drive
archivo = drive.CreateFile({'title': nombre_archivo_backup, 'parents': [{'id': CARPETA_DRIVE}]})
archivo.SetContentFile(zip_path)
archivo.Upload()
print(f"Archivo de backup '{nombre_archivo_backup}' subido con éxito a Google Drive.")
