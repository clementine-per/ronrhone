from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse_lazy
from django.utils import timezone

from gestion_association.models import TypeChoice, OuiNonChoice
from gestion_association.models.animal import Preference, Animal, SexeChoice, TypeVaccinChoice
from medical_visit.models import VisiteMedicale, TypeVisiteVetoChoice


class MedicalVisitModelTestCase(TestCase):
    def setUp(self):
        preference_one = Preference.objects.create()
        Animal.objects.create(
            nom="Twix",
            sexe=SexeChoice.F.name,
            circonstances="Abandon",
            sterilise=OuiNonChoice.NON.name,
            preference=preference_one,
        )
        preference_two = Preference.objects.create()
        Animal.objects.create(
            nom="Cerise",
            sexe=SexeChoice.F.name,
            circonstances="Abandon",
            sterilise=OuiNonChoice.NON.name,
            preference=preference_two,
        )

    def test_amount_per_animal(self):
        visite = VisiteMedicale.objects.create(date=timezone.now(), visit_type=TypeVisiteVetoChoice.AUTRE.name,
                                      amount=Decimal(200))
        for animal in Animal.objects.all():
            visite.animals.add(animal)
        self.assertEqual(visite.get_amount_per_animal(), Decimal(100))

    def test_save_with_sterilisation(self):
        animal = Animal.objects.get(nom="Twix")
        self.assertEqual(OuiNonChoice.NON.name, animal.sterilise)
        visite = VisiteMedicale.objects.create(date=timezone.now().date()+timedelta(days=2),
                                               visit_type=TypeVisiteVetoChoice.STE.name,
                                               amount=Decimal(200))
        visite.animals.add(animal)
        visite.save()
        # Get the updated animal fresh from database
        animal = Animal.objects.get(nom="Twix")
        self.assertEqual(OuiNonChoice.OUI.name, animal.sterilise)
        self.assertEqual(timezone.now().date()+timedelta(days=2), animal.date_sterilisation)

    def test_save_with_first_vaccine(self):
        animal_one = Animal.objects.get(nom="Twix")
        animal_two = Animal.objects.get(nom="Cerise")
        visite = VisiteMedicale.objects.create(date=timezone.now().date() + timedelta(days=2),
                                               visit_type=TypeVisiteVetoChoice.PACK_TC.name,
                                               amount=Decimal(200))
        visite.animals.add(animal_one)
        visite.animals.add(animal_two)
        visite.save()
        # Get the updated animals fresh from database
        animal_one = Animal.objects.get(nom="Twix")
        animal_two = Animal.objects.get(nom="Cerise")
        self.assertEqual(OuiNonChoice.OUI.name, animal_one.primo_vaccine)
        self.assertEqual(OuiNonChoice.OUI.name, animal_two.primo_vaccine)
        self.assertEqual(OuiNonChoice.NON.name, animal_one.vaccin_ok)
        self.assertEqual(OuiNonChoice.NON.name, animal_two.vaccin_ok)
        self.assertEqual(timezone.now().date() + timedelta(days=2), animal_one.date_dernier_vaccin)
        self.assertEqual(TypeVaccinChoice.TC.name, animal_two.type_vaccin)

    def test_save_with_full_vaccine(self):
        animal = Animal.objects.get(nom="Twix")
        visite = VisiteMedicale.objects.create(date=timezone.now().date() + timedelta(days=2),
                                               visit_type=TypeVisiteVetoChoice.VAC_RAPPEL_TCL.name,
                                               amount=Decimal(200))
        visite.animals.add(animal)
        visite.save()
        # Get the updated animal fresh from database
        animal = Animal.objects.get(nom="Twix")
        self.assertEqual(OuiNonChoice.OUI.name, animal.vaccin_ok)
        self.assertEqual(timezone.now().date() + timedelta(days=2), animal.date_dernier_vaccin)
        self.assertEqual(TypeVaccinChoice.TCL.name, animal.type_vaccin)


class MedicalVisitViewTestCase(TestCase):
    def setUp(self):
        self.today = timezone.now().date()
        self.client = Client()
        self.user = User.objects.create_superuser("temporary", "temporary@gmail.com", "temporary")
        self.client.login(username="temporary", password="temporary")
        preference_one = Preference.objects.create()
        animal_one = Animal.objects.create(
            nom="Twix",
            sexe=SexeChoice.F.name,
            circonstances="Abandon",
            sterilise=OuiNonChoice.NON.name,
            preference=preference_one,
        )
        preference_two = Preference.objects.create()
        animal_two = Animal.objects.create(
            nom="Cerise",
            sexe=SexeChoice.F.name,
            circonstances="Abandon",
            sterilise=OuiNonChoice.NON.name,
            preference=preference_two,
        )
        visite = VisiteMedicale.objects.create(date=self.today,
                                               visit_type=TypeVisiteVetoChoice.VAC_RAPPEL_TCL.name,
                                               amount=Decimal(200), veterinary="clinique bellecour")
        visite.animals.add(animal_one)
        visite.animals.add(animal_two)
        visite.save()

    def test_visit_list_view(self):
        response = self.client.get(reverse_lazy("visites"))
        self.assertContains(response, "Cerise")
        self.assertContains(response, "Twix")
        self.assertContains(response, "Rappel")
        self.assertContains(response, "200")

    def test_visit_list_view_filters(self):
        url_root = "/ronrhone/medical_visits/list/"
        # Veterinary filter
        response = self.client.get(f"{url_root}?veterinary=bellecour")
        self.assertContains(response, "clinique bellecour")
        response = self.client.get(f"{url_root}?veterinary=test")
        self.assertNotContains(response, "clinique bellecour")
        # Visit type filter
        response = self.client.get(f"{url_root}?visit_type={TypeVisiteVetoChoice.VAC_RAPPEL_TCL.name}")
        self.assertContains(response, "clinique bellecour")
        response = self.client.get(f"{url_root}?visit_type={TypeVisiteVetoChoice.STE.name}")
        self.assertNotContains(response, "clinique bellecour")
        # Date filters
        tomorrow_str = (self.today + timedelta(days=1)).strftime("%Y-%m-%d")
        yesterday_str = (self.today - timedelta(days=1)).strftime("%Y-%m-%d")
        response = self.client.get(f"{url_root}?date_min={yesterday_str}&date_max={tomorrow_str}")
        self.assertContains(response, "clinique bellecour")
        response = self.client.get(f"{url_root}?date_min={tomorrow_str}")
        self.assertNotContains(response, "clinique bellecour")

    def test_visit_delete_view(self):
        self.assertEquals(VisiteMedicale.objects.all().count(), 1)
        self.client.get(reverse_lazy("delete_visite",
                        args=[VisiteMedicale.objects.get(visit_type=TypeVisiteVetoChoice.VAC_RAPPEL_TCL.name).pk]))
        self.assertEquals(VisiteMedicale.objects.all().count(), 0)
