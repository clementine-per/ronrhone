import sys
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from gestion_association.forms.adoption import (
    AdoptionCreateFormNoAdoptant,
    AdoptionCreateForm,
    AdoptionFromUserForm,
    AdoptionUpdateForm,
    ShowBonForm,
    BonSterilisationForm,
)
from gestion_association.forms.person import PersonForm
from gestion_association.models.adoption import (
    Adoption,
    TarifAdoption,
    TarifBonSterilisation,
    BonSterilisation,
)
from gestion_association.models.animal import Animal, StatutAnimal
from gestion_association.models.person import Person


@login_required
def index(request, pk):
    animal = Animal.objects.get(id=pk)
    title = "Adoption de " + animal.nom
    return render(request, "gestion_association/adoption/choix_adoption.html", locals())


@login_required
def adoption_complete(request, pk):
    animal = Animal.objects.get(id=pk)
    title = "Adoption de " + animal.nom
    if request.method == "POST":
        person_form = PersonForm(data=request.POST)
        adoption_form = AdoptionCreateFormNoAdoptant(data=request.POST)
        bon_form = BonSterilisationForm(data=request.POST)
        show_bon_form = ShowBonForm(data=request.POST)
        if person_form.is_valid() and adoption_form.is_valid():
            # Récupération des éléments
            person = person_form.save()
            adoption = adoption_form.save(commit=False)

            save_adoption(adoption, animal, person, show_bon_form, bon_form)

            return redirect("detail_animal", pk=animal.id)

    else:
        person_form = PersonForm()
        show_bon_form = ShowBonForm(initial={"show": "NON"})
        adoption_form = AdoptionCreateFormNoAdoptant()
        bon_form = BonSterilisationForm()
        montant_adoption = get_montant_adoption(animal)
        if montant_adoption:
            adoption_form.fields["montant"].initial = montant_adoption
            adoption_form.fields["montant_restant"].initial = montant_adoption

    return render(
        request, "gestion_association/adoption/adoption_complete.html", locals()
    )


@login_required
def adoption_allegee(request, pk):
    animal = Animal.objects.get(id=pk)
    title = "Adoption de " + animal.nom
    if request.method == "POST":
        adoption_form = AdoptionCreateForm(data=request.POST)
        show_bon_form = ShowBonForm(data=request.POST)
        bon_form = BonSterilisationForm(data=request.POST)
        if adoption_form.is_valid():

            adoption = adoption_form.save(commit=False)
            save_adoption(adoption, animal, adoption.adoptant, show_bon_form, bon_form)

            return redirect("detail_animal", pk=animal.id)

    else:
        adoption_form = AdoptionCreateForm()
        show_bon_form = ShowBonForm(initial={"show": "NON"})
        bon_form = BonSterilisationForm()
        montant_adoption = get_montant_adoption(animal)
        if montant_adoption:
            adoption_form.fields["montant"].initial = montant_adoption
            adoption_form.fields["montant_restant"].initial = montant_adoption

    return render(
        request, "gestion_association/adoption/adoption_allegee.html", locals()
    )


@login_required
def adoption_from_user(request, pk):
    person = Person.objects.get(id=pk)
    title = "Adoption par " + person.prenom + " " + person.nom
    if request.method == "POST":
        adoption_form = AdoptionFromUserForm(data=request.POST)
        show_bon_form = ShowBonForm(data=request.POST)
        bon_form = BonSterilisationForm(data=request.POST)
        if adoption_form.is_valid():
            adoption = adoption_form.save(commit=False)
            save_adoption(adoption, adoption.animal, person, show_bon_form, bon_form)

            return redirect("detail_animal", pk=adoption.animal.id)

    else:
        adoption_form = AdoptionFromUserForm()
        show_bon_form = ShowBonForm(initial={"show": "NON"})
        bon_form = BonSterilisationForm()

    return render(
        request, "gestion_association/adoption/adoption_from_user.html", locals()
    )


class UpdateAdoption(LoginRequiredMixin, UpdateView):
    model = Adoption
    form_class = AdoptionUpdateForm
    template_name = "gestion_association/adoption/adoption_form.html"

    def get_success_url(self):
        return reverse_lazy("detail_animal", kwargs={"pk": self.object.animal.id})


class UpdateBonSterilisation(LoginRequiredMixin, UpdateView):
    model = BonSterilisation
    form_class = BonSterilisationForm
    template_name = "gestion_association/adoption/bon_form.html"

    def get_success_url(self):
        return reverse_lazy(
            "detail_animal", kwargs={"pk": self.object.adoption.animal.id}
        )


def get_montant_adoption(animal):
    # Méthode récupérant le montant de l'adoption à l'initialisation du formulaire
    try:
        preselection_tarifs = TarifAdoption.objects.filter(
            type_animal=animal.type, sexe=animal.sexe, tranche_age=animal.tranche_age
        )
        preselection_tarifs = preselection_tarifs.filter(
            Q(sterilise=animal.sterilise) | Q(sterilise="")
        )
        print("Apres sterilisation")
        print(preselection_tarifs)
        preselection_tarifs = preselection_tarifs.filter(
            Q(vaccin_ok=animal.vaccin_ok) | Q(vaccin_ok="")
        )
        print("Apres vaccin")
        print(preselection_tarifs)
        sys.stdout.flush()
        tarif_applicable = preselection_tarifs.first()
        return tarif_applicable.montant
    except TarifAdoption.DoesNotExist:
        return None


def calcul_montant_restant(request):
    # Méthode de calcul dynamique du montant restant en fonction de l'acompte
    montant_adoption = Decimal(0)
    montant_restant = Decimal(0)
    # Récupération des données utiles au calcul
    montant_actuel_str = request.POST["montant"]
    montant_restant_str = request.POST["montant_restant"]
    acompte_verse_input = request.POST["acompte_verse"]
    if montant_restant_str:
        montant_restant = Decimal(montant_restant_str)
    if montant_actuel_str:
        montant_adoption = Decimal(montant_actuel_str)
    # Application de l'acompte de 100 euros si necessaire
    if montant_actuel_str and acompte_verse_input and acompte_verse_input == "OUI":
        montant_restant = montant_adoption - Decimal(100)
    # Application du prix du bon de stérilisation
    # Renvoyer vue json
    return JsonResponse(
        {
            "montant": montant_adoption,
            "montant_restant": montant_restant.max(Decimal(0)),
        }
    )


def calcul_montant_sterilisation(request, pk):
    animal = Animal.objects.get(id=pk)
    montant_adoption = Decimal(0)
    montant_restant = Decimal(0)
    # Récupération des données utiles au calcul
    montant_actuel_str = request.POST["montant"]
    montant_restant_str = request.POST["montant_restant"]
    if montant_restant_str:
        montant_restant = Decimal(montant_restant_str)
    if montant_actuel_str:
        montant_adoption = Decimal(montant_actuel_str)
    bon_input = request.POST["show"]
    montant_bon = TarifBonSterilisation.objects.get(
        type_animal=animal.type, sexe=animal.sexe
    ).montant
    if montant_actuel_str and bon_input and bon_input == "OUI":
        montant_adoption = Decimal(montant_actuel_str) + montant_bon
        montant_restant = montant_restant + montant_bon
    if montant_actuel_str and bon_input and bon_input == "NON":
        montant_adoption = Decimal(montant_actuel_str) - montant_bon
        montant_restant = montant_restant - montant_bon
    return JsonResponse(
        {
            "montant": montant_adoption.max(Decimal(0)),
            "montant_restant": montant_restant.max(Decimal(0)),
        }
    )


def save_adoption(adoption, animal, person, show_form, bon_form):
    # La personne devient adoptante
    person.is_adoptante = True
    person.save()
    # On rattache la personne à l'adoption
    adoption.adoptant = person
    adoption.animal = animal
    adoption.save()
    # l'animal passe au statut à en cours d'adoption
    animal.statut = StatutAnimal.ADOPTION
    animal.adoptant = person
    # Gestion du bon de stérilisation uniquement si necessaire
    if animal.sterilise == "NON":
        show_form.is_valid()
        show_bon = show_form.cleaned_data["show"]
        if show_bon == "OUI" and bon_form.is_valid():
            bon = bon_form.save(commit=False)
            bon.adoption = adoption
            bon.save()
