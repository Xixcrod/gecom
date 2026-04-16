# services.py
import os
import shutil
import zipfile
from django.conf import settings
from django.db import connections
from .backup_utils import upload_or_replace_backup, download_latest_backup

def perform_system_backup():
    """Ejecuta toda la lógica de compresión y subida del respaldo."""
    temp_dir = os.path.join(settings.BASE_DIR, 'temp_backup_folder')
    if os.path.exists(temp_dir): 
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    # 1. Copiar db.sqlite3 y la carpeta media
    shutil.copy2(os.path.join(settings.BASE_DIR, 'db.sqlite3'), temp_dir)
    shutil.copytree(settings.MEDIA_ROOT, os.path.join(temp_dir, 'media'), dirs_exist_ok=True)

    # 2. Comprimir
    zip_base_path = os.path.join(settings.BASE_DIR, 'current_backup')
    final_zip = shutil.make_archive(zip_base_path, 'zip', temp_dir)

    # 3. Subir
    upload_or_replace_backup(final_zip)

    # 4. Limpiar basura local
    shutil.rmtree(temp_dir)
    os.remove(final_zip)


def perform_system_restore():
    """Ejecuta la descarga, extracción y reemplazo de los archivos de Prisma."""
    lock_path = os.path.join(settings.BASE_DIR, 'maintenance.lock')
    try:
        # 1. ACTIVAR MANTENIMIENTO
        open(lock_path, 'a').close()

        # 2. Descargar respaldo
        zip_path = download_latest_backup()
        if not zip_path:
            raise Exception("No se encontró el archivo de respaldo en Google Drive.")

        extract_path = os.path.join(settings.BASE_DIR, 'temp_restore_folder')
        if os.path.exists(extract_path):
            shutil.rmtree(extract_path)
            
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)

        # 3. PREPARAR EL REEMPLAZO DE BASE DE DATOS
        for conn in connections.all():
            conn.close()
        
        new_db = os.path.join(extract_path, 'db.sqlite3')
        old_db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')

        if os.path.exists(new_db):
            if os.path.exists(old_db_path):
                os.remove(old_db_path) 
            shutil.move(new_db, old_db_path)

        # 4. Reemplazar Carpeta Media
        new_media = os.path.join(extract_path, 'media')
        if os.path.exists(new_media):
            if os.path.exists(settings.MEDIA_ROOT):
                shutil.rmtree(settings.MEDIA_ROOT)
            shutil.move(new_media, settings.MEDIA_ROOT)

        # 5. Limpiar archivos temporales
        shutil.rmtree(extract_path)
        if os.path.exists(zip_path):
            os.remove(zip_path)
            
    finally:
        # 6. DESACTIVAR MANTENIMIENTO SIEMPRE
        if os.path.exists(lock_path):
            os.remove(lock_path)