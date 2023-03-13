import tempfile

import PyPDF2
from dateutil.relativedelta import relativedelta
from django.test import TestCase
from django.utils import timezone

from reportlab.pdfgen import canvas

from contract.utils import header, next_page, get_data_certified_engagement, personal_infos, infos_animal, info_prices, \
    info_vaccine_shot, info_sterilisation
from gestion_association.models import TypeChoice, OuiNonChoice
from gestion_association.models.adoption import Adoption
from gestion_association.models.animal import Preference, Animal, SexeChoice, TrancheAge, StatutAnimal
from gestion_association.models.person import Person


class ContractGenerationTestCase(TestCase):
    def setUp(self):
        person = Person.objects.create(
            nom="DOE",
            prenom="John",
            email="johndoe@gmail.com",
            is_famille=False,
            is_adoptante=True,
            is_benevole=False,
            adresse="5 rue des idéaux",
            code_postal="10000",
            ville="Lyon",
        )
        preference_chaton = Preference.objects.create()
        twix = Animal.objects.create(
            nom="Twix",
            sexe=SexeChoice.F.name,
            type=TypeChoice.CHAT.name,
            circonstances="Abandon",
            sterilise=OuiNonChoice.NON.name,
            preference=preference_chaton,
            tranche_age= TrancheAge.ENFANT.name,
            adoptant= person,
            statut=StatutAnimal.ADOPTION.name
        )
        preference_adulte = Preference.objects.create()
        cerise = Animal.objects.create(
            nom="Cerise",
            sexe=SexeChoice.F.name,
            type=TypeChoice.CHAT.name,
            circonstances="Abandon",
            sterilise=OuiNonChoice.OUI.name,
            preference=preference_adulte,
            tranche_age=TrancheAge.ADULTE.name,
            adoptant=person,
            statut=StatutAnimal.ADOPTION.name
        )

        Adoption.objects.create(
            adoptant=person,
            animal=cerise
        )

        Adoption.objects.create(
            adoptant=person,
            animal=twix
        )

    def test_next_page(self):
        temp_file = tempfile.NamedTemporaryFile()
        p = canvas.Canvas(temp_file)
        nb_page = 1
        nb_page = next_page(p, nb_page)
        next_page(p, nb_page)
        p.save()
        reader = PyPDF2.PdfFileReader(temp_file)
        self.assertEqual(reader.numPages, 2)
        text = reader.pages[0].extract_text()
        self.assertIn("Association Ron’Rhône", text)

    def test_header_chaton(self):
        temp_file = tempfile.NamedTemporaryFile()
        p = canvas.Canvas(temp_file)
        animal = Animal.objects.get(nom="Twix")
        header(p, animal)
        p.save()
        reader = PyPDF2.PdfFileReader(temp_file)
        self.assertEqual(reader.numPages, 1)
        text = reader.pages[0].extract_text()
        self.assertIn("Twix", text)
        self.assertIn("CHATON", text)

    def test_header_adulte(self):
        temp_file = tempfile.NamedTemporaryFile()
        p = canvas.Canvas(temp_file)
        animal = Animal.objects.get(nom="Cerise")
        header(p, animal)
        p.save()
        reader = PyPDF2.PdfFileReader(temp_file)
        self.assertEqual(reader.numPages, 1)
        text = reader.pages[0].extract_text()
        self.assertIn("Cerise", text)
        self.assertIn("ADULTE", text)

    def test_data_certified_engagement(self):
        animal = Animal.objects.get(nom="Twix")
        certificat_engagement_data = get_data_certified_engagement(animal)
        reader = PyPDF2.PdfFileReader(certificat_engagement_data)
        text = reader.pages[0].extract_text()
        self.assertIn("John", text)
        self.assertIn("DOE", text)
        self.assertIn("Lyon", text)

    def test_personal_infos(self):
        temp_file = tempfile.NamedTemporaryFile()
        p = canvas.Canvas(temp_file)
        animal = Animal.objects.get(nom="Cerise")
        personal_infos(p, animal)
        p.save()
        reader = PyPDF2.PdfFileReader(temp_file)
        self.assertEqual(reader.numPages, 1)
        text = reader.pages[0].extract_text()
        self.assertIn("John", text)
        self.assertIn("DOE", text)
        self.assertIn("Lyon", text)

    def test_infos_animal(self):
        temp_file = tempfile.NamedTemporaryFile()
        p = canvas.Canvas(temp_file)
        animal = Animal.objects.get(nom="Twix")
        infos_animal(p, animal)
        p.save()
        reader = PyPDF2.PdfFileReader(temp_file)
        self.assertEqual(reader.numPages, 1)
        text = reader.pages[0].extract_text()
        self.assertIn("Nom du chaton", text)
        self.assertIn("Twix", text)
        self.assertIn("Sexe : F", text)

    def test_info_prices_child(self):
        temp_file = tempfile.NamedTemporaryFile()
        p = canvas.Canvas(temp_file)
        animal = Animal.objects.get(nom="Twix")
        info_prices(p, animal)
        p.save()
        reader = PyPDF2.PdfFileReader(temp_file)
        self.assertEqual(reader.numPages, 1)
        text = reader.pages[0].extract_text()
        self.assertIn("Primo vaccination", text)
        self.assertNotIn("Stérilisation", text)

    def test_info_prices_adult(self):
        temp_file = tempfile.NamedTemporaryFile()
        p = canvas.Canvas(temp_file)
        animal = Animal.objects.get(nom="Cerise")
        info_prices(p, animal)
        p.save()
        reader = PyPDF2.PdfFileReader(temp_file)
        self.assertEqual(reader.numPages, 1)
        text = reader.pages[0].extract_text()
        self.assertIn("180€", text)

    def test_info_vaccine_shot_no_info(self):
        temp_file = tempfile.NamedTemporaryFile()
        p = canvas.Canvas(temp_file)
        animal = Animal.objects.get(nom="Twix")
        info_vaccine_shot(p, animal)
        p.save()
        reader = PyPDF2.PdfFileReader(temp_file)
        self.assertEqual(reader.numPages, 1)
        text = reader.pages[0].extract_text()
        self.assertIn("__/__/__", text)

    def test_info_vaccine_shot_vaccine_ok(self):
        temp_file = tempfile.NamedTemporaryFile()
        p = canvas.Canvas(temp_file)
        animal = Animal.objects.get(nom="Twix")
        animal.vaccin_ok = OuiNonChoice.OUI.name
        animal.date_dernier_vaccin = timezone.now().date()
        next_vaccine = animal.date_dernier_vaccin + relativedelta(years=1)
        next_vaccine_str = next_vaccine.strftime("%d/%m/%Y")
        info_vaccine_shot(p, animal)
        p.save()
        reader = PyPDF2.PdfFileReader(temp_file)
        self.assertEqual(reader.numPages, 1)
        text = reader.pages[0].extract_text()
        self.assertIn(next_vaccine_str, text)
        self.assertIn("peu de temps avant le", text)

    def test_info_sterilisation(self):
        temp_file = tempfile.NamedTemporaryFile()
        p = canvas.Canvas(temp_file)
        animal = Animal.objects.get(nom="Twix")
        animal.date_naissance = timezone.now().date() - relativedelta(months=7)
        info_sterilisation(p, animal)
        p.save()
        reader = PyPDF2.PdfFileReader(temp_file)
        self.assertEqual(reader.numPages, 1)
        text = reader.pages[0].extract_text()
        self.assertIn(timezone.now().date().strftime("%d/%m/%Y"), text)