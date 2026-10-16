#!/usr/bin/env bash
#Salir si ocurre algún error
set -o errexit

#Actualizar pip a la última versión
python -m pip install --upgrade pip

#Instalar dependencias
pip install -r requirements/production.txt

#Recolectar archivos estáticos para Supabase
python manage.py collectstatic --noinput

#Ejecutar migraciones en la base de datos de Neon
python manage.py migrate

#Crear el superusuario (si no existen)
python create_super_user.py