import os
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from django.conf import settings

def get_drive_instance():
    gauth = GoogleAuth()
    cred_file = os.path.join(settings.BASE_DIR, "credentials.json")
    
    # Cargar la configuración del cliente
    GoogleAuth.DEFAULT_SETTINGS['client_config_file'] = os.path.join(settings.BASE_DIR, 'client_secrets.json')
    
    # Intentar cargar credenciales existentes
    if os.path.exists(cred_file):
        gauth.LoadCredentialsFile(cred_file)

    if not gauth.credentials:
        # SI NO HAY CREDENCIALES:
        # Configuramos el acceso offline y el consentimiento antes de llamar a la función
        gauth.GetAuthUrl() # Genera la URL base internamente
        gauth.LocalWebserverAuth() 
    elif gauth.access_token_expired:
        # SI EXPIRARON: Intentar refrescar
        try:
            gauth.Refresh()
        except Exception:
            # Si falla el refresco, forzamos un nuevo inicio de sesión
            gauth.LocalWebserverAuth()
    else:
        # SI TODO ESTÁ BIEN: Autorizar
        gauth.Authorize()
        
    # Guardar siempre las credenciales actualizadas
    gauth.SaveCredentialsFile(cred_file)
    return GoogleDrive(gauth)

def upload_or_replace_backup(file_path):
    drive = get_drive_instance()
    filename = 'gecom_backup_total.zip'
    
    file_list = drive.ListFile({'q': f"title='{filename}' and trashed=false"}).GetList()
    
    if file_list:
        drive_file = file_list[0] # Reemplaza el existente
    else:
        drive_file = drive.CreateFile({'title': filename}) # Crea uno nuevo
    
    drive_file.SetContentFile(file_path)
    drive_file.Upload()
    return drive_file['id']

def download_latest_backup():
    drive = get_drive_instance()
    filename = 'gecom_backup_total.zip'
    file_list = drive.ListFile({'q': f"title='{filename}' and trashed=false"}).GetList()
    
    if not file_list:
        return None
    
    drive_file = file_list[0]
    local_path = os.path.join(settings.BASE_DIR, 'temp_download.zip')
    drive_file.GetContentFile(local_path)
    return local_path