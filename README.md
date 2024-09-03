# Script Backup automatico con python

## Este script se encarga de crear un backup de la carpeta "archivos" y subirla a Google Drive.
### El nombre del archivo se generará según el día de la semana:
    ### - Si es sábado, el nombre del archivo será "backup_semanal_<fecha_actual>.zip"
    ### - Si no es sábado, el nombre del archivo será "backup_diario.zip"

## El script verificará si el archivo ya existe en Google Drive y lo eliminará si es necesario.
## Finalmente, se creará y subirá el archivo a Google Drive.
