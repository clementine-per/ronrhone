from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from gestion_association.forms.animal import AnimalSearchForm


@login_required()
def search_animal(request):
    form = AnimalSearchForm()
    selected = "animals"
    return render(request, "gestion_association/animal_list.html", locals())