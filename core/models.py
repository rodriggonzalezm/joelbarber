from datetime import datetime,timedelta
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

class Shop(models.Model):
    name=models.CharField(max_length=120,default="Joel Barber & Tattoo")
    address=models.CharField(max_length=180,default="Córdoba 33, Plottier, Neuquén")
    phone=models.CharField(max_length=30,default="0299 656-5853")
    instagram=models.CharField(max_length=80,default="joelbarbershop25")
    slot_minutes=models.PositiveIntegerField(default=60)
    def __str__(self):return self.name

class Service(models.Model):
    shop=models.ForeignKey(Shop,on_delete=models.CASCADE,related_name="services")
    name=models.CharField(max_length=100);description=models.CharField(max_length=220,blank=True)
    price=models.DecimalField(max_digits=10,decimal_places=2);duration_minutes=models.PositiveIntegerField(default=60)
    active=models.BooleanField(default=True)
    def __str__(self):return self.name

class Barber(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name="barber")
    shop=models.ForeignKey(Shop,on_delete=models.CASCADE,related_name="barbers")
    display_name=models.CharField(max_length=80);bio=models.CharField(max_length=180,blank=True)
    phone=models.CharField(max_length=30,blank=True);is_owner=models.BooleanField(default=False);active=models.BooleanField(default=True)
    def __str__(self):return self.display_name

class WorkSchedule(models.Model):
    DAYS=[(0,"Lunes"),(1,"Martes"),(2,"Miércoles"),(3,"Jueves"),(4,"Viernes"),(5,"Sábado"),(6,"Domingo")]
    barber=models.ForeignKey(Barber,on_delete=models.CASCADE,related_name="schedules")
    weekday=models.PositiveSmallIntegerField(choices=DAYS);start_time=models.TimeField();end_time=models.TimeField();active=models.BooleanField(default=True)
    class Meta:unique_together=("barber","weekday")

class Appointment(models.Model):
    STATUS=[("confirmed","Confirmado"),("completed","Atendido"),("cancelled","Cancelado"),("noshow","No asistió")]
    shop=models.ForeignKey(Shop,on_delete=models.CASCADE,related_name="appointments")
    barber=models.ForeignKey(Barber,on_delete=models.PROTECT,related_name="appointments")
    service=models.ForeignKey(Service,on_delete=models.PROTECT,related_name="appointments")
    customer_name=models.CharField(max_length=100);customer_phone=models.CharField(max_length=30);customer_email=models.EmailField(blank=True)
    date=models.DateField();start_time=models.TimeField();status=models.CharField(max_length=20,choices=STATUS,default="confirmed")
    notes=models.CharField(max_length=240,blank=True);created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=["barber","date","start_time"],condition=~models.Q(status="cancelled"),name="unique_active_barber_slot")]
        ordering=["date","start_time"]
    @property
    def end_time(self):
        return (datetime.combine(self.date,self.start_time)+timedelta(minutes=self.service.duration_minutes)).time()
    def clean(self):
        schedule=self.barber.schedules.filter(weekday=self.date.weekday(),active=True).first()
        if not schedule or self.start_time<schedule.start_time or self.end_time>schedule.end_time:raise ValidationError("El horario está fuera de la jornada del profesional.")
        clash=Appointment.objects.filter(barber=self.barber,date=self.date,start_time=self.start_time).exclude(status="cancelled").exclude(pk=self.pk)
        if clash.exists():raise ValidationError("Ese horario ya fue reservado.")
