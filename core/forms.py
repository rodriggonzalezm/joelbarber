from django import forms
from django.contrib.auth.models import User
from .models import Appointment,Barber,Service

class SetupForm(forms.Form):
    username=forms.CharField(label="Usuario administrador");email=forms.EmailField(label="Email")
    password=forms.CharField(label="Contraseña",widget=forms.PasswordInput);display_name=forms.CharField(label="Nombre visible",initial="Joel")
    def clean_username(self):
        v=self.cleaned_data["username"]
        if User.objects.filter(username=v).exists():raise forms.ValidationError("Ese usuario ya existe.")
        return v

class BookingForm(forms.ModelForm):
    class Meta:
        model=Appointment;fields=["service","barber","date","start_time","customer_name","customer_phone","customer_email","notes"]
        labels={"service":"Servicio","barber":"Profesional","date":"Fecha","start_time":"Horario","customer_name":"Tu nombre","customer_phone":"WhatsApp","customer_email":"Email (opcional)","notes":"¿Querés contarnos algo?"}
        widgets={"date":forms.DateInput(attrs={"type":"date","min":""}),"start_time":forms.Select(choices=[]),"notes":forms.TextInput(attrs={"placeholder":"Ej: degradé bajo"})}
    def __init__(self,*a,shop=None,**kw):
        super().__init__(*a,**kw);self.shop=shop
        self.fields["service"].queryset=shop.services.filter(active=True)
        self.fields["barber"].queryset=shop.barbers.filter(active=True)
        self.fields["start_time"].widget.choices=[("","Elegí fecha y profesional")]
        if self.data.get("start_time"):self.fields["start_time"].widget.choices=[(self.data["start_time"],self.data["start_time"])]
    def clean(self):
        data=super().clean()
        if data.get("date") and data["date"]<__import__('datetime').date.today():self.add_error("date","Elegí una fecha futura.")
        return data

class StaffForm(forms.Form):
    display_name=forms.CharField(label="Nombre visible");username=forms.CharField(label="Usuario")
    email=forms.EmailField(label="Email",required=False);password=forms.CharField(label="Contraseña inicial",widget=forms.PasswordInput)
    phone=forms.CharField(label="Teléfono",required=False);bio=forms.CharField(label="Especialidad",required=False)
    def clean_username(self):
        v=self.cleaned_data["username"]
        if User.objects.filter(username=v).exists():raise forms.ValidationError("Ese usuario ya existe.")
        return v

class ServiceForm(forms.ModelForm):
    class Meta:
        model=Service;fields=["name","description","price","duration_minutes","active"]
        labels={"name":"Servicio","description":"Descripción","price":"Precio","duration_minutes":"Duración (minutos)","active":"Disponible"}

class AppointmentStatusForm(forms.ModelForm):
    class Meta:model=Appointment;fields=["status","notes"]
