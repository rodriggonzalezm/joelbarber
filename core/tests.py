from datetime import date,time
from django.test import TestCase
from django.urls import reverse
from .models import Appointment,Barber,Service,Shop,WorkSchedule

class BookingTests(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User
        self.shop=Shop.objects.first();self.service=self.shop.services.first()
        user=User.objects.create_user("joel",password="clave")
        self.barber=Barber.objects.create(user=user,shop=self.shop,display_name="Joel",is_owner=True)
        WorkSchedule.objects.create(barber=self.barber,weekday=0,start_time=time(10),end_time=time(13))

    def payload(self,slot="10:00"):
        return {"service":self.service.id,"barber":self.barber.id,"date":"2026-06-22","start_time":slot,"customer_name":"Cliente","customer_phone":"2995555555","customer_email":"","notes":""}

    def test_booking_and_double_booking_protection(self):
        response=self.client.post(reverse("booking"),self.payload())
        self.assertEqual(response.status_code,302);self.assertEqual(Appointment.objects.count(),1)
        response=self.client.post(reverse("booking"),self.payload())
        self.assertEqual(response.status_code,200);self.assertTrue(response.context["form"].errors)
        self.assertEqual(Appointment.objects.count(),1)

    def test_slots_api_hides_booked_hour(self):
        Appointment.objects.create(shop=self.shop,barber=self.barber,service=self.service,customer_name="Ana",customer_phone="123",date=date(2026,6,22),start_time=time(10))
        response=self.client.get(reverse("slots_api"),{"barber":self.barber.id,"date":"2026-06-22","service":self.service.id})
        self.assertEqual(response.json()["slots"],["11:00","12:00"])

    def test_owner_and_barber_access(self):
        self.client.login(username="joel",password="clave")
        self.assertEqual(self.client.get(reverse("dashboard")).status_code,200)
        self.assertEqual(self.client.get(reverse("staff_list")).status_code,200)

    def test_setup_is_locked_after_owner_exists(self):
        self.assertRedirects(self.client.get(reverse("setup")),reverse("login"))
