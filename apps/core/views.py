from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.urls import reverse

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

