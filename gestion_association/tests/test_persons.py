from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse_lazy

from gestion_association.models.person import Person


def create_person(nom, prenom, mail, is_famille, is_adoptante, is_benevole):
    return Person.objects.create(
        nom=nom,
        prenom=prenom,
        email=mail,
        is_famille=is_famille,
        is_adoptante=is_adoptante,
        is_benevole=is_benevole,
        adresse="5 rue des idéaux",
        code_postal="10000",
        ville="Lyon",
    )


class PersonListTests(TestCase):
    def setUp(self):
        create_person("MINCH", "Clémentine", "test.test@gmail.com", True, True, False)
        create_person("JANNE", "Vincent", "test.ertt@gmail.com", False, True, True)
        self.client = Client()
        self.user = User.objects.create_superuser("temporary", "temporary@gmail.com", "temporary")
        self.client.login(username="temporary", password="temporary")

    def test_person_list_view(self):
        response = self.client.get(reverse_lazy("persons"))
        self.assertContains(response, "MINCH")
        self.assertContains(response, "JANNE")

    def test_person_list_filter(self):
        # Test filtre sur le nom
        response_nom = self.client.get("/ronrhone/persons/?nom=nc")
        self.assertContains(response_nom, "MINCH")
        self.assertNotContains(response_nom, "JANNE")

        # Test filtre sur le rôle
        response_role = self.client.get("/ronrhone/persons/?type_person=BENEVOLE")
        self.assertContains(response_role, "JANNE")
        self.assertNotContains(response_role, "MINCH")


class PersonCreateUpdateTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser("temporary", "temporary@gmail.com", "temporary")
        self.client.login(username="temporary", password="temporary")

    def test_create_person(self):
        self.client.post('/ronrhone/persons/create', {'prenom': 'Elise', 'nom': 'FIGMA', 'email': 'adresse@gmail.com',
                                                      'adresse': '10 rue de la joie', 'code_postal' : '69003', 'ville' : 'Lyon',
                                                      'telephone' : '0380502635'})
        response_nom = self.client.get("/ronrhone/persons/?nom=fi")
        self.assertContains(response_nom, "FIGMA")

    def test_update_person(self):
        person = create_person("MINCH", "Clémentine", "test.test@gmail.com", False, False, False)
        # Vérification de l'accès au formulaire de modification d'une personne
        response = self.client.post(reverse_lazy("update_person", kwargs={"pk": person.id}))
        self.assertEqual(response.status_code, 200)


class PersonOtherViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser("temporary", "temporary@gmail.com", "temporary")
        self.client.login(username="temporary", password="temporary")

    def test_declarer_benevole_person(self):
        person = create_person("MINCH", "Clémentine", "test.test@gmail.com", False, False, False)

        self.client.post(reverse_lazy("benevole_person", kwargs={"pk": person.id}),
                                    {'commentaire_benevole' : 'Nouvelle bénévole'})
        response = self.client.get(reverse_lazy("detail_person", kwargs={"pk": person.id}))
        query_person = Person.objects.get(id=person.id)
        self.assertEqual(query_person.is_benevole, True)
        self.assertContains(response, "Nouvelle bénévole")

    def test_annule_benevole(self):
        person = create_person("MINCH", "Clémentine", "test.test@gmail.com", False, False, True)
        self.client.get(reverse_lazy("cancel_benevole", kwargs={"pk": person.id}))
        query_person = Person.objects.get(id=person.id)
        self.assertEqual(query_person.is_benevole, False)
