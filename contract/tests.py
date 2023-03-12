import tempfile

import PyPDF2
from django.test import TestCase

# Create your tests here.
from reportlab.pdfgen import canvas

from contract.utils import header, next_page, get_data_certified_engagement, personal_infos, infos_animal
from gestion_association.models import TypeChoice, OuiNonChoice
from gestion_association.models.animal import Preference, Animal, SexeChoice, TrancheAge
from gestion_association.models.person import Person


class ContractGenerationTestCase(TestCase):
    def setUp(self):
        person = Person.objects.create(
            nom="DOE",
            prenom="John",
            email="johndoe@gmail.com",
            is_famille=False,
            is_adoptante=False,
            is_benevole=False,
            adresse="5 rue des idéaux",
            code_postal="10000",
            ville="Lyon",
        )
        preference_chaton = Preference.objects.create()
        Animal.objects.create(
            nom="Twix",
            sexe=SexeChoice.F.name,
            type=TypeChoice.CHAT.name,
            circonstances="Abandon",
            sterilise=OuiNonChoice.NON.name,
            preference=preference_chaton,
            tranche_age= TrancheAge.ENFANT.name,
            adoptant= person
        )
        preference_adulte = Preference.objects.create()
        Animal.objects.create(
            nom="Cerise",
            sexe=SexeChoice.F.name,
            type=TypeChoice.CHAT.name,
            circonstances="Abandon",
            sterilise=OuiNonChoice.OUI.name,
            preference=preference_adulte,
            tranche_age=TrancheAge.ADULTE.name,
            adoptant=person
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