from django.contrib.auth.decorators import login_required
from django.urls import path
from django.views.generic import DetailView

from .models.person import Person
from .views import (home, animal, person)

urlpatterns = [
    path("", home.index, name="accueil"),
    path("animals/", animal.search_animal, name="animals"),
    path("persons/create", person.CreatePerson.as_view(), name="create_person"),
    path("persons/update/<int:pk>/", person.UpdatePerson.as_view(), name="update_person"),
    path("persons/update/benevole/<int:pk>/", person.BenevolePerson.as_view(), name="benevole_person"),
    path("persons/", person.person_list, name="persons"),
    path("persons/<int:pk>/", login_required(DetailView.as_view(model=Person)), name="detail_person"),]