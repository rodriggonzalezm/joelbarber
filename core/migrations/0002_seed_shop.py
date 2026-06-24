from django.db import migrations

def seed(apps,schema_editor):
    Shop=apps.get_model("core","Shop");Service=apps.get_model("core","Service")
    shop=Shop.objects.create(name="Joel Barber & Tattoo",address="Córdoba 33, Plottier, Neuquén",phone="0299 656-5853",instagram="joelbarbershop25",slot_minutes=60)
    Service.objects.bulk_create([
        Service(shop=shop,name="Corte clásico",description="Corte personalizado, terminaciones precisas y styling.",price=12000,duration_minutes=60),
        Service(shop=shop,name="Corte + barba",description="Servicio completo de corte, perfilado y cuidado de barba.",price=17000,duration_minutes=60),
        Service(shop=shop,name="Barba premium",description="Perfilado, toalla caliente y terminación profesional.",price=10000,duration_minutes=60),
    ])

def unseed(apps,schema_editor):apps.get_model("core","Shop").objects.filter(name="Joel Barber & Tattoo").delete()
class Migration(migrations.Migration):
    dependencies=[("core","0001_initial")]
    operations=[migrations.RunPython(seed,unseed)]
