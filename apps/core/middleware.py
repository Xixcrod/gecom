import os
from django.conf import settings
from django.shortcuts import render

''' Middleware para modo de mantenimiento - Si el archivo 'maintenance.lock' existe en la raíz del proyecto, se mostrará una página de mantenimiento a los usuarios.'''
class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lock_file = os.path.join(settings.BASE_DIR, 'maintenance.lock')

        if os.path.exists(lock_file):
            # Si el archivo existe, mostramos la pantalla de mantenimiento
            return render(request, 'maintenance.html', status=503)

        return self.get_response(request)