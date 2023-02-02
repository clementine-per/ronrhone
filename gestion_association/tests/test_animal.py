from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse_lazy
from django.utils import timezone

from gestion_association.models import TypeChoice, OuiNonChoice
from gestion_association.models.animal import Animal, SexeChoice, Preference, StatutAnimal, TestResultChoice
from gestion_association.models.famille import Famille
from gestion_association.models.person import Person


def create_animal_simple(nom):
    # Création d'un animal
    preference = Preference.objects.create()
    return Animal.objects.create(
        nom=nom,
        sexe=OuiNonChoice.OUI.name,
        type=TypeChoice.CHAT.name,
        circonstances="Abandon",
        sterilise=OuiNonChoice.OUI.name,
        preference=preference,
    )

def create_animal_complexe(nom, sexe, type, sterilise, statut, identification, date_naissance,
                           date_prochain_vaccin, fa, fiv_felv):
    # Création d'un animal
    preference = Preference.objects.create()
    famille = None
    if fa:
        person = Person.objects.create(
            nom="CHAT",
            prenom="Elise",
            email="aa@aa.fr",
            is_famille=True,
            is_adoptante=False,
            is_benevole=False,
            adresse="5 rue des idéaux",
            code_postal="10000",
            ville="Lyon",
        )
        famille = Famille.objects.create(personne=person, nb_places=3)
    return Animal.objects.create(
        nom=nom,
        sexe=sexe,
        type=type,
        circonstances="Abandon",
        sterilise=sterilise,
        preference=preference,
        famille=famille,
        statut=statut,
        identification=identification,
        date_naissance=date_naissance,
        date_prochain_vaccin=date_prochain_vaccin,
        fiv=fiv_felv,
        felv=fiv_felv,
    )


class AnimalListTests(TestCase):

    def setUp(self):
        self.today = timezone.now().date()
        interval_10 = self.today - timedelta(days=10)
        create_animal_complexe("Cerise", SexeChoice.F.name, TypeChoice.CHAT.name, OuiNonChoice.OUI.name,
                               StatutAnimal.SOCIA.name,"id5526",interval_10,interval_10,True,
                               TestResultChoice.POSITIVE.name)
        create_animal_complexe("Twix", SexeChoice.M.name, TypeChoice.CHIEN.name, OuiNonChoice.NON.name,
                               StatutAnimal.ADOPTABLE.name, "id8826", self.today, self.today, False,
                               TestResultChoice.NT.name)
        self.client = Client()
        self.user = User.objects.create_user("temporary", "temporary@gmail.com", "temporary")
        self.client.login(username="temporary", password="temporary")

    def test_animal_list_view(self):
        response = self.client.get(reverse_lazy("animals"))
        self.assertContains(response, "Cerise")

    def test_person_list_filter(self):
        # Test filtre sur le nom
        response = self.client.get("/ronrhone/animals/?nom=wi")
        self.assertContains(response, "Twix")
        self.assertNotContains(response, "Cerise")

        # Test filtre sur le type
        response = self.client.get("/ronrhone/animals/?type=CHIEN")
        self.assertContains(response, "Twix")
        self.assertNotContains(response, "Cerise")

        # Test filtre sur sterilise
        response = self.client.get("/ronrhone/animals/?sterilise=OUI")
        self.assertContains(response, "Cerise")
        self.assertNotContains(response, "Twix")

        # Test filtre sur identification
        response = self.client.get("/ronrhone/animals/?identification=55")
        self.assertContains(response, "Cerise")
        self.assertNotContains(response, "Twix")

        # Test filtre sur statuts
        response = self.client.get("/ronrhone/animals/?statuts=SOCIA")
        self.assertContains(response, "Cerise")
        self.assertNotContains(response, "Twix")
        response = self.client.get("/ronrhone/animals/?statuts=SOCIA&statuts=ADOPTABLE")
        self.assertContains(response, "Cerise")
        self.assertContains(response, "Twix")

        # Test date de naissance
        tomorrow_str = (self.today + timedelta(days=1)).strftime("%Y-%m-%d")
        yesterday_str = (self.today - timedelta(days=1)).strftime("%Y-%m-%d")
        url = f"/ronrhone/animals/?date_naissance_min={yesterday_str}&date_naissance_max={tomorrow_str}"
        response = self.client.get(url)
        self.assertContains(response, "Twix")
        self.assertNotContains(response, "Cerise")
        url = f"/ronrhone/animals/?date_naissance_max={tomorrow_str}"
        response = self.client.get(url)
        self.assertContains(response, "Cerise")
        self.assertContains(response, "Twix")

        # Test prochain vaccin
        tomorrow_str = (self.today + timedelta(days=1)).strftime("%Y-%m-%d")
        yesterday_str = (self.today - timedelta(days=1)).strftime("%Y-%m-%d")
        url = f"/ronrhone/animals/?date_prochain_vaccin_min={yesterday_str}&date_prochain_vaccin_max={tomorrow_str}"
        response = self.client.get(url)
        self.assertContains(response, "Twix")
        self.assertNotContains(response, "Cerise")
        url = f"/ronrhone/animals/?date_prochain_vaccin_max={tomorrow_str}"
        response = self.client.get(url)
        self.assertContains(response, "Cerise")
        self.assertContains(response, "Twix")

        # Test filtre sur fa
        response = self.client.get("/ronrhone/animals/?sans_fa=NON")
        self.assertContains(response, "Cerise")
        self.assertNotContains(response, "Twix")

        # Test filtre sur fa
        response = self.client.get("/ronrhone/animals/?fiv_felv=OUI")
        self.assertContains(response, "Cerise")
        self.assertNotContains(response, "Twix")

class AnimalCreateUpdateTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("temporary", "temporary@gmail.com", "temporary")
        self.client.login(username="temporary", password="temporary")

    def test_create_animal(self):
        self.client.post('/ronrhone/animals/create', {'nom': 'Violette', 'sexe': SexeChoice.F.name,
                                                      'type': TypeChoice.CHAT.name, 'circonstances' : 'Abandon', 'statut' : StatutAnimal.SOCIA.name,
                                                      'sterilise' : OuiNonChoice.OUI.name, 'primo_vaccine' : OuiNonChoice.OUI.name, 'vaccin_ok' : OuiNonChoice.OUI.name,
                                                      'fiv' : TestResultChoice.NT.name, 'felv': TestResultChoice.NT.name,
                                                      'sociabilisation' : OuiNonChoice.NON.name, 'exterieur' : OuiNonChoice.NON.name, 'quarantaine' : OuiNonChoice.NON.name,
                                                      'biberonnage' : OuiNonChoice.NON.name})
        response = self.client.get(reverse_lazy("animals"))
        self.assertContains(response, "Violette")

    def test_update_animal(self):
        animal = create_animal_simple("Pinky")
        # Vérification de l'accès au formulaire de modification des préférences d'un animal
        response = self.client.post(reverse_lazy("update_preference", kwargs={"pk": animal.id}))
        self.assertEqual(response.status_code, 200)
        # Vérification de l'accès au formulaire de modification des infos principales d'un animal
        response = self.client.post(reverse_lazy("update_information", kwargs={"pk": animal.id}))
        self.assertEqual(response.status_code, 200)
        # Vérification de l'accès au formulaire de modification des infos de santé d'un animal
        response = self.client.post(reverse_lazy("update_sante", kwargs={"pk": animal.id}))
        self.assertEqual(response.status_code, 200)