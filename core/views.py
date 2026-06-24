from datetime import date,time
from urllib.parse import quote as urlquote
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError,transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404,redirect,render
from .forms import AppointmentStatusForm,BookingForm,ServiceForm,SetupForm,StaffForm,WorkScheduleForm
from .models import Appointment,Barber,Service,Shop,WorkSchedule
from .utils import available_slots

def shop():return Shop.objects.first()
def home(request):return render(request,"home.html",{"shop":shop()})

@transaction.atomic
def setup(request):
    s=shop()
    if s.barbers.filter(is_owner=True).exists():return redirect("login")
    form=SetupForm(request.POST or None)
    if request.method=="POST" and form.is_valid():
        u=User.objects.create_user(form.cleaned_data["username"],form.cleaned_data["email"],form.cleaned_data["password"],is_staff=True)
        b=Barber.objects.create(user=u,shop=s,display_name=form.cleaned_data["display_name"],is_owner=True)
        for day in range(6):WorkSchedule.objects.create(barber=b,weekday=day,start_time=time(10),end_time=time(20))
        login(request,u);return redirect("dashboard")
    return render(request,"form.html",{"form":form,"title":"Activar el sistema","button":"Crear acceso administrador"})

@transaction.atomic
def booking(request):
    s=shop();form=BookingForm(request.POST or None,shop=s)
    if request.method=="POST" and form.is_valid():
        appt=form.save(commit=False);appt.shop=s
        try:appt.full_clean();appt.save()
        except (IntegrityError,ValidationError):form.add_error("start_time","Ese horario acaba de ocuparse. Elegí otro.")
        else:return redirect("booking_success",appt.pk)
    return render(request,"booking.html",{"form":form,"shop":s})

def slots_api(request):
    try:
        b=Barber.objects.get(pk=request.GET["barber"],active=True);d=date.fromisoformat(request.GET["date"]);service=Service.objects.filter(pk=request.GET.get("service")).first()
    except (KeyError,ValueError,Barber.DoesNotExist):return JsonResponse({"slots":[]})
    return JsonResponse({"slots":[x.strftime("%H:%M") for x in available_slots(b,d,service)]})

def booking_success(request,pk):
    a=get_object_or_404(Appointment,pk=pk)
    text=urlquote(f"Hola, soy {a.customer_name}. Reservé {a.service.name} con {a.barber.display_name} para el {a.date:%d/%m} a las {a.start_time:%H:%M}.")
    return render(request,"success.html",{"appointment":a,"whatsapp":f"https://wa.me/5492996565853?text={text}"})

@login_required
def dashboard(request):
    s=request.user.barber.shop;selected=request.GET.get("date",date.today().isoformat());day=date.fromisoformat(selected)
    qs=s.appointments.filter(date=day).select_related("barber","service")
    if not request.user.barber.is_owner:qs=qs.filter(barber=request.user.barber)
    return render(request,"dashboard.html",{"appointments":qs,"selected":selected,"is_owner":request.user.barber.is_owner,"barbers":s.barbers.filter(active=True)})

@login_required
def appointment_detail(request,pk):
    a=get_object_or_404(Appointment.objects.select_related("barber","service"),pk=pk,shop=request.user.barber.shop)
    if not request.user.barber.is_owner and a.barber!=request.user.barber:return redirect("dashboard")
    form=AppointmentStatusForm(request.POST or None,instance=a)
    if request.method=="POST" and form.is_valid():form.save();messages.success(request,"Turno actualizado.");return redirect("appointment_detail",pk)
    return render(request,"appointment.html",{"appointment":a,"form":form})

@login_required
def staff_list(request):
    if not request.user.barber.is_owner:return redirect("dashboard")
    return render(request,"staff.html",{"barbers":request.user.barber.shop.barbers.all()})

@login_required
@transaction.atomic
def staff_create(request):
    if not request.user.barber.is_owner:return redirect("dashboard")
    form=StaffForm(request.POST or None)
    if request.method=="POST" and form.is_valid():
        u=User.objects.create_user(form.cleaned_data["username"],form.cleaned_data["email"],form.cleaned_data["password"])
        b=Barber.objects.create(user=u,shop=request.user.barber.shop,display_name=form.cleaned_data["display_name"],phone=form.cleaned_data["phone"],bio=form.cleaned_data["bio"])
        for day in range(6):WorkSchedule.objects.create(barber=b,weekday=day,start_time=time(10),end_time=time(20))
        messages.success(request,"Profesional agregado con agenda propia.");return redirect("staff_list")
    return render(request,"form.html",{"form":form,"title":"Agregar profesional","button":"Crear acceso"})

@login_required
def schedule_list(request):
    me=request.user.barber
    s=me.shop
    is_owner=me.is_owner

    if is_owner:
        selected_id=request.POST.get("barber") or request.GET.get("barber")
        selected_barber=s.barbers.filter(pk=selected_id).first() if selected_id else me
    else:
        selected_barber=me

    form=WorkScheduleForm(
        request.POST or None,
        shop=s,
        current_barber=me,
        is_owner=is_owner,
        initial={"barber":selected_barber,"active":True},
    )

    if request.method=="POST" and form.is_valid():
        target=form.get_barber()
        if not is_owner and target!=me:
            return redirect("dashboard")
        WorkSchedule.objects.update_or_create(
            barber=target,
            weekday=form.cleaned_data["weekday"],
            defaults={
                "start_time":form.cleaned_data["start_time"],
                "end_time":form.cleaned_data["end_time"],
                "active":form.cleaned_data["active"],
            },
        )
        messages.success(request,"Horario guardado correctamente.")
        return redirect(f"{request.path}?barber={target.pk}" if is_owner else request.path)

    schedules_by_day={x.weekday:x for x in selected_barber.schedules.all()}
    rows=[]
    for value,label in WorkSchedule.DAYS:
        rows.append({"weekday":value,"label":label,"schedule":schedules_by_day.get(value)})

    return render(request,"schedules.html",{
        "form":form,
        "rows":rows,
        "selected_barber":selected_barber,
        "barbers":s.barbers.filter(active=True).order_by("display_name"),
        "is_owner":is_owner,
    })

@login_required
def service_list(request):
    if not request.user.barber.is_owner:return redirect("dashboard")
    return render(request,"services.html",{"services":request.user.barber.shop.services.all()})
@login_required
def service_edit(request,pk=None):
    if not request.user.barber.is_owner:return redirect("dashboard")
    obj=get_object_or_404(Service,pk=pk,shop=request.user.barber.shop) if pk else None;form=ServiceForm(request.POST or None,instance=obj)
    if request.method=="POST" and form.is_valid():x=form.save(commit=False);x.shop=request.user.barber.shop;x.save();return redirect("service_list")
    return render(request,"form.html",{"form":form,"title":"Editar servicio" if obj else "Nuevo servicio","button":"Guardar"})
