from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from .utils.servicios_respaldo import perform_system_backup, perform_system_restore
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

@login_required
def trigger_backup(request):
    '''Ejecuta la lógica de respaldo y muestra mensajes de éxito o error.'''
    try:
        perform_system_backup()
        messages.success(request, "El respaldo se ha guardado en Google Drive con éxito.")
    except Exception as e:
        messages.error(request, f"Error al crear el respaldo: {str(e)}")
    
    return redirect('respaldo') 


@login_required
def trigger_restore(request):
    '''Ejecuta la lógica de restauración y muestra mensajes de éxito o error.'''
    try:
        perform_system_restore(request)
        messages.success(request, "Sistema restaurado correctamente.")
    except Exception as e:
        messages.error(request, f"Error en restauración: {str(e)}")
    
    return redirect('login')

