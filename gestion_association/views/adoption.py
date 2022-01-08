import sys
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse
from django.utils.dateparse import parse_date
from django.views.generic import UpdateView

from gestion_association.forms.adoption import (
    AdoptionCreateForm,
    AdoptionCreateFormNoAdoptant,
    AdoptionFromUserForm,
    AdoptionUpdateForm,
    BonSterilisationForm,
    ShowBonForm,
    AdoptionSearchForm)
from gestion_association.forms.person import PersonForm
from gestion_association.models.adoption import (
    Adoption,
    BonSterilisation,
    TarifAdoption,
    TarifBonSterilisation,
)
from gestion_association.models.animal import Animal, StatutAnimal
from gestion_association.models.person import Person


@login_required
def index(request, pk):
    animal = Animal.objects.get(id=pk)
    title = "Adoption de " + animal.nom
    return render(request, "gestion_association/adoption/choix_adoption.html", locals())


@login_required()
def search_adoption(request):
    adoptions = Adoption.objects.all()
    selected = "adoptions"
    title = "Liste des adoptions"

    if request.method == "POST":
        form = AdoptionSearchForm(request.POST)
        if form.is_valid():
            base_url = reverse('adoptions')
            query_string = form.data.urlencode()
            url = '{}?{}'.format(base_url, query_string)
            return redirect(url)
    else:
        form = AdoptionSearchForm()
        montant_restant_form =request.GET.get("montant_restant", "")
        animal_form = request.GET.get("animal", "")
        pre_visite_form = request.GET.get("pre_visite", "")
        visite_controle_form = request.GET.getlist("visite_controle", "")
        date_min_form = request.GET.get("date_min", "")
        date_max_form = request.GET.get("date_max", "")
        statut_form = request.GET.get("statut", "")
        date_expiration_min_form = request.GET.get("date_expiration_min", "")
        date_expiration_max_form = request.GET.get("date_expiration_max", "")
        bon_envoye_form = request.GET.get("bon_envoye", "")
        bon_utilise_form = request.GET.get("bon_utilise", "")
        # champ hors formulaire, uniquement parametre url depuis TDB
        acompte_verse = request.GET.get("acompte_verse", "")
        sterilise = request.GET.get("sterilise", "")
        date_visite_max = request.GET.get("date_visite_max", "")
        date_naissance_max = request.GET.get("date_naissance_max", "")

        if montant_restant_form:
            form.fields["montant_restant"].initial = montant_restant_form
            adoptions = adoptions.filter(montant_restant__gt=int(montant_restant_form))
        if animal_form:
            form.fields["animal"].initial = animal_form
            adoptions = adoptions.filter(animal__nom__icontains=animal_form)
        if pre_visite_form:
            form.fields["pre_visite"].initial = pre_visite_form
            adoptions = adoptions.filter(pre_visite=pre_visite_form)
        if visite_controle_form:
            form.fields["visite_controle"].initial = visite_controle_form
            adoptions = adoptions.filter(visite_controle__in=visite_controle_form)
        if date_min_form:
            form.fields["date_min"].initial = date_min_form
            adoptions = adoptions.filter(date__gte=parse_date(date_min_form))
        if date_max_form:
            form.fields["date_max"].initial = date_max_form
            adoptions = adoptions.filter(date__lte=parse_date(date_max_form))
        if statut_form:
            form.fields["statut"].initial = statut_form
            adoptions = adoptions.filter(animal__statut=statut_form)
        if date_expiration_min_form:
            form.fields["date_expiration_min"].initial = date_expiration_min_form
            adoptions = adoptions.filter(bon__date_max__gte=parse_date(date_expiration_min_form))
        if date_expiration_max_form:
            form.fields["date_expiration_max"].initial = date_expiration_max_form
            adoptions = adoptions.filter(bon__date_max__lte=parse_date(date_expiration_max_form))
        if bon_envoye_form:
            form.fields["bon_envoye"].initial = bon_envoye_form
            adoptions = adoptions.filter(bon__envoye=bon_envoye_form)
        if bon_utilise_form:
            form.fields["bon_utilise"].initial = bon_utilise_form
            adoptions = adoptions.filter(bon__utilise=bon_utilise_form)
        if acompte_verse:
            adoptions = adoptions.filter(acompte_verse=acompte_verse)
        if sterilise:
            adoptions = adoptions.filter(animal__sterilise=sterilise)
        if date_visite_max:
            adoptions = adoptions.filter(date_visite__lte=date_visite_max)
        if date_naissance_max:
            adoptions = adoptions.filter(animal__date_naissance__lte=date_naissance_max)



    # Pagination : 20 éléments par page
    paginator = Paginator(adoptions.order_by("-date"), 20)
    nb_results = adoptions.count()
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        adoption_list = paginator.page(page)
    except EmptyPage:
        # Si on dépasse la limite de pages, on prend la dernière
        adoption_list = paginator.page(paginator.num_pages())

    return render(request, "gestion_association/adoption/adoption_list.html", locals())


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

    return render(request, "gestion_association/adoption/adoption_complete.html", locals())


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

    return render(request, "gestion_association/adoption/adoption_allegee.html", locals())


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

    return render(request, "gestion_association/adoption/adoption_from_user.html", locals())


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
        return reverse_lazy("detail_animal", kwargs={"pk": self.object.adoption.animal.id})

@login_required
def create_bon_sterilisation(request, pk):
    adoption = Adoption.objects.get(id=pk)
    title = "Ajout d'un bon de stérilisation"
    if request.method == "POST":
        form = BonSterilisationForm(data=request.POST)
        if form.is_valid():
            bon = form.save(commit=False)
            bon.adoption = adoption
            bon.save()
            adoption.save()
            return redirect("detail_animal", pk=adoption.animal.id)

    else:
        form = BonSterilisationForm()

    return render(request, "gestion_association/adoption/bon_form.html", locals())


def get_montant_adoption(animal):
    # Méthode récupérant le montant de l'adoption à l'initialisation du formulaire

    preselection_tarifs = TarifAdoption.objects.filter(
        type_animal=animal.type, sexe=animal.sexe, tranche_age=animal.tranche_age
    )
    preselection_tarifs = preselection_tarifs.filter(
        Q(sterilise=animal.sterilise) | Q(sterilise="")
    )
    preselection_tarifs = preselection_tarifs.filter(
        Q(vaccin_ok=animal.vaccin_ok) | Q(vaccin_ok="")
    )

    tarif_applicable = preselection_tarifs.first()
    if tarif_applicable :
        return tarif_applicable.montant
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
    try:
        montant_bon = TarifBonSterilisation.objects.get(
            type_animal=animal.type, sexe=animal.sexe
        ).montant
        if montant_actuel_str and bon_input and bon_input == "OUI":
            montant_adoption = Decimal(montant_actuel_str) + montant_bon
            montant_restant = montant_restant + montant_bon
        if montant_actuel_str and bon_input and bon_input == "NON":
            montant_adoption = Decimal(montant_actuel_str) - montant_bon
            montant_restant = montant_restant - montant_bon
    finally:
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
    animal.statut = StatutAnimal.ADOPTION.name
    animal.adoptant = person
    animal.save()
    # Gestion du bon de stérilisation uniquement si necessaire
    if animal.sterilise == "NON":
        show_form.is_valid()
        show_bon = show_form.cleaned_data["show"]
        if show_bon == "OUI" and bon_form.is_valid():
            bon = bon_form.save(commit=False)
            bon.adoption = adoption
            bon.save()
