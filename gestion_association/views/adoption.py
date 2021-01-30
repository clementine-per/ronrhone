from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from gestion_association.forms.adoption import AdoptionCreateFormNoAdoptant, AdoptionCreateForm
from gestion_association.forms.person import PersonForm
from gestion_association.models.animal import Animal, StatutAnimal


@login_required
def index(request, pk):
    animal = Animal.objects.get(id=pk)
    return render(request, "gestion_association/adoption/choix_adoption.html", locals())

@login_required
def adoption_complete(request, pk):
    animal = Animal.objects.get(id=pk)
    if request.method == "POST":
        person_form = PersonForm(data=request.POST)
        adoption_form = AdoptionCreateFormNoAdoptant(data=request.POST)
        if (
            person_form.is_valid()
            and adoption_form.is_valid()
        ):
            # Enregistrement de la personne
            person = person_form.save()
            person.is_adoptante = True
            person.save()

            # On rattache la personne à l'adoption
            adoption = adoption_form.save(commit=False)
            adoption.adoptant = person
            adoption.animal = animal
            adoption.save()

            # l'animal passe au statut à en cours d'adoption
            animal.statut = StatutAnimal.ADOPTION

            adoption.save()

            return redirect("detail_animal", pk=animal.id)

    else:
        person_form = PersonForm()
        adoption_form = AdoptionCreateFormNoAdoptant()

    return render(request, "gestion_association/adoption/adoption_complete.html", locals())


@login_required
def adoption_allegee(request, pk):
    animal = Animal.objects.get(id=pk)
    if request.method == "POST":
        adoption_form = AdoptionCreateForm(data=request.POST)
        if adoption_form.is_valid():
            
            new_adoption = adoption_form.save(commit=False)

            # l'animal passe au statut à en cours d'adoption
            animal.statut = StatutAnimal.ADOPTION.name
            new_adoption.animal = animal
            person = new_adoption.adoptant
            person.is_adoptante =True
            person.save()
            new_adoption.save()
            animal.save()

            return redirect("detail_animal", pk=animal.id)

    else:
        adoption_form = AdoptionCreateForm()

    return render(request, "gestion_association/adoption/adoption_allegee.html", locals())