from django.contrib import admin
from .models import Appointment,Barber,Service,Shop,WorkSchedule
admin.site.register([Appointment,Barber,Service,Shop,WorkSchedule])
