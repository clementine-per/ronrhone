from django.contrib.auth.decorators import login_required
from django.urls import path
from django.views.generic import DetailView

from .models.animal import Animal
from .models.famille import Famille
from .models.person import Person
from .views import (home, animal, person, adoption, famille)

urlpatterns = [
    path("", home.index, name="accueil"),
    # Animaux
    path("animals/", animal.CreateAnimal.as_view(), name="create_animal"),
    path("animals/create", animal.search_animal, name="animals"),
    path("animals/prefrence/update/<int:pk>/", animal.UpdatePreference.as_view(), name="update_preference"),
    path("animals/information/update/<int:pk>/", animal.UpdateInformation.as_view(), name="update_information"),
    path("animals/sante/update/<int:pk>/", animal.UpdateSante.as_view(), name="update_sante"),
    path("animals/<int:pk>/", login_required(
        DetailView.as_view(model=Animal, template_name="gestion_association/animal/animal_detail.html")),
         name="detail_animal"),
    # Personnes
    path("persons/create", person.CreatePerson.as_view(), name="create_person"),
    path("persons/update/<int:pk>/", person.UpdatePerson.as_view(), name="update_person"),
    path("persons/update/benevole/<int:pk>/", person.BenevolePerson.as_view(), name="benevole_person"),
    path("persons/cancel/benevole/<int:pk>/", person.person_benevole_cancel, name="cancel_benevole"),
    path("persons/", person.person_list, name="persons"),
    path("persons/<int:pk>/", login_required(
        DetailView.as_view(model=Person, template_name="gestion_association/person/person_detail.html")),
         name="detail_person"),
    # Adoptions
    path("adoption/<int:pk>/", adoption.index, name="adoption"),
    path(
        "adoption_complete/<int:pk>/",
        adoption.adoption_complete,
        name="adoption_complete",
    ),
    path(
        "adoption_allegee/<int:pk>/",
        adoption.adoption_allegee,
        name="adoption_allegee",
    ),
    #Familles
    path("familles/create/<int:pk>/", famille.create_famille, name="create_famille"),
    path("familles/", famille.famille_list, name="familles"),
    path("familles/<int:pk>/", login_required(
        DetailView.as_view(model=Famille, template_name="gestion_association/famille/famille_detail.html")),
         name="detail_famille"),
    ]