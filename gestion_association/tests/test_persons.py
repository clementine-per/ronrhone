import sys

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse_lazy

from gestion_association.models.person import Person


def create_person(nom, prenom, mail, is_famille, is_adoptante, is_benevole):
    # Création d'une personne
    person = Person.objects.create(nom=nom, prenom=prenom, email=mail, is_famille=is_famille, is_adoptante=is_adoptante,
                    is_benevole=is_benevole, adresse="5 rue des idéaux", code_postal="10000", ville="Lyon")
    return person

class PersonListTests(TestCase):
    def setUp(self):
        create_person("MINCH","Clémentine", "test.test@gmail.com", True, True, False)
        create_person("JANNE", "Vincent", "test.ertt@gmail.com", False, True, True)
        self.client = Client()
        self.user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        self.client.login(username='temporary', password='temporary')

    def test_person_list_view(self):
        response = self.client.get(reverse_lazy('persons'))
        self.assertContains(response, "MINCH")
        self.assertContains(response, "JANNE")

    def test_person_list_filter(self):
        # Test filtre sur le nom
        response_nom = self.client.post(
            "/ronrhone/persons/", data={"nom": "nc"}
        )
        self.assertContains(response_nom, "MINCH")
        self.assertNotContains(response_nom, "JANNE")

        # Test filtre sur le rôle
        response_role = self.client.post(
            "/ronrhone/persons/", data={"type_person": "BENEVOLE"}
        )
        self.assertContains(response_role, "JANNE")
        self.assertNotContains(response_role, "MINCH")


class PersonCreateUpdateTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        self.client.login(username='temporary', password='temporary')

    def test_create_person(self):
        # Vérification de l'accès au formulaire de création d'une personne
        response = self.client.get(reverse_lazy('create_person'))
        self.assertEqual(response.status_code, 200)

    def test_update_person(self):
        person = create_person("MINCH","Clémentine", "test.test@gmail.com", True, True, False)
        # Vérification de l'accès au formulaire de modification d'une personne
        response = self.client.get(reverse_lazy('update_person', kwargs={"pk": person.id}))
        self.assertEqual(response.status_code, 200)
