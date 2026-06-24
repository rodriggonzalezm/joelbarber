# Joel Barber & Tattoo — sistema de reservas

Aplicación Django personalizada para Joel Barber & Tattoo, Córdoba 33, Plottier, Neuquén.

## Funcionalidad

- Landing moderna y responsive con identidad visual propia.
- Reserva pública por servicio, profesional, fecha y horario.
- Turnos base de una hora y horarios configurables por barbero.
- Bloqueo de dobles reservas a nivel de aplicación y base de datos.
- Múltiples barberos, cada uno con usuario y agenda propia.
- Dueño con acceso a todas las agendas, servicios y equipo.
- Estados: confirmado, atendido, cancelado y no asistió.
- Confirmación por WhatsApp.
- Servicios y precios editables.
- Panel administrativo Django.
- Imagen editorial original generada para este proyecto.
- Suite de pruebas automatizadas.

## Primer inicio

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

1. Abrí `http://127.0.0.1:8000/activar/` y creá el usuario dueño.
2. Ingresá al panel y agregá profesionales.
3. Revisá servicios, precios y horarios antes de publicar.

Los datos públicos precargados provienen del perfil de Google Maps suministrado por el cliente. Los precios son demostrativos y deben confirmarse con el negocio.

## Producción

Configurar PostgreSQL, HTTPS, dominio, copias de seguridad, email transaccional, política de privacidad y `SECRET_KEY`. Los recordatorios automáticos de WhatsApp requieren Meta WhatsApp Cloud API o un proveedor autorizado.
