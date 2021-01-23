from django.contrib.auth.decorators import login_required
from django.urls import path
from django.views.generic import DetailView

from .models.animal import Animal
from .models.person import Person
from .views import (home, animal, person)

urlpatterns = [
    path("", home.index, name="accueil"),
    path("animals/", animal.CreateAnimal.as_view(), name="create_animal"),
    path("animals/create", animal.search_animal, name="animals"),
    path("animals/prefrence/update/<int:pk>/", animal.UpdatePreference.as_view(), name="update_preference"),
    path("animals/information/update/<int:pk>/", animal.UpdateInformation.as_view(), name="update_information"),
    path("animals/sante/update/<int:pk>/", animal.UpdateSante.as_view(), name="update_sante"),
    path("animals/<int:pk>/", login_required(
        DetailView.as_view(model=Animal, template_name="gestion_association/animal/animal_detail.html")),
         name="detail_animal"),
    path("persons/create", person.CreatePerson.as_view(), name="create_person"),
    path("persons/update/<int:pk>/", person.UpdatePerson.as_view(), name="update_person"),
    path("persons/update/benevole/<int:pk>/", person.BenevolePerson.as_view(), name="benevole_person"),
    path("persons/", person.person_list, name="persons"),
    path("persons/<int:pk>/", login_required(DetailView.as_view(model=Person)), name="detail_person"),]