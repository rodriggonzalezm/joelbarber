from datetime import datetime,timedelta
from .models import Appointment

def available_slots(barber,date,service=None):
    schedule=barber.schedules.filter(weekday=date.weekday(),active=True).first()
    if not schedule:return []
    duration=service.duration_minutes if service else barber.shop.slot_minutes
    cursor=datetime.combine(date,schedule.start_time);end=datetime.combine(date,schedule.end_time);slots=[]
    busy=set(Appointment.objects.filter(barber=barber,date=date).exclude(status="cancelled").values_list("start_time",flat=True))
    while cursor+timedelta(minutes=duration)<=end:
        if cursor.time() not in busy:slots.append(cursor.time())
        cursor+=timedelta(minutes=barber.shop.slot_minutes)
    return slots
