from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from .utils.servicios_respaldo import perform_system_backup, perform_system_restore
from django.conf import settings
import os
import socket

# Create your views here.
def signin(request):
    return render(request, 'login.html')

def recuperar_contrasena(request):
    return render(request, 'recuperar_contrasena.html')

def nueva_contrasena(request):
    return render(request, 'nueva_contrasena.html')

@login_required
def signout(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))

@login_required
def respaldo(request):
    return render(request, 'respaldo.html')


def tiene_conexion_internet(host="8.8.8.8", port=53, timeout=3):
    """
    Verifica si la PC local tiene conexión externa a internet.
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False

@login_required
def trigger_backup(request):
    '''Ejecuta la lógica de respaldo y muestra mensajes de éxito o error.'''

    # 1. VALIDACIÓN DE INTERNET
    if not tiene_conexion_internet():
        messages.error(request, "Error: No tienes conexión a internet. Es requerida para subir el respaldo a Google Drive.")
        return redirect('respaldo')
    
    try:
        perform_system_backup()
        messages.success(request, "El respaldo se ha guardado en Google Drive con éxito.")
    except Exception as e:
        messages.error(request, f"Error al crear el respaldo: {str(e)}")
    
    return redirect('respaldo') 


@login_required
def trigger_restore(request):
    '''Ejecuta la lógica de restauración y muestra mensajes de éxito o error.'''
    
    #1. Verificación de pre-requisitos
    client_secrets = os.path.join(settings.BASE_DIR, 'client_secrets.json')
    if not os.path.exists(client_secrets):
        messages.error(request, "Error: Falta el archivo client_secrets.json.")
        return redirect('respaldo')
    
    # 2. VALIDACIÓN DE INTERNET (Crítica antes de bloquear el sistema)
    if not tiene_conexion_internet():
        messages.error(request, "Error: No tienes conexión a internet. Es requerida para descargar el respaldo desde Google Drive.")
        return redirect('respaldo')
    
    try:
        perform_system_restore(request)
        messages.success(request, "Sistema restaurado correctamente.")
    except Exception as e:
        messages.error(request, f"Error en restauración: {str(e)}")
        return redirect('respaldo')
    
    return redirect('login')

