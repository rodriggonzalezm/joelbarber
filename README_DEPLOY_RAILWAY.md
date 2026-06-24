# Deploy en Railway

Proyecto Django preparado para Railway con Gunicorn, WhiteNoise y PostgreSQL.

## Subir a GitHub

```powershell
cd C:\ruta\del\proyecto

git init
git branch -M main
git add .
git commit -m "Deploy inicial Joel Barber"
git remote add origin https://github.com/rodriggonzalezm/joelbarber.git
git push -u origin main
```

Si el repositorio ya tenía commits:

```powershell
git remote set-url origin https://github.com/rodriggonzalezm/joelbarber.git
git push -u origin main
```

## Variables en Railway

Agregar estas variables en el servicio Django:

```env
SECRET_KEY=una-clave-larga-y-segura
DEBUG=0
ALLOWED_HOSTS=.railway.app
```

Al agregar PostgreSQL en Railway, usar la variable `DATABASE_URL` que Railway provee.

## Inicio luego del deploy

1. Abrir la URL pública de Railway.
2. Entrar a `/activar/`.
3. Crear el usuario dueño.
4. Cargar profesionales y revisar servicios/precios.

El `Procfile` ejecuta automáticamente migraciones, collectstatic y Gunicorn.
