import json
import sys

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage, Paginator
from django.db.models import Count, F
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView, View

from gestion_association.forms import PreferenceForm
from gestion_association.forms.animal import AnimalSelectForFaForm
from gestion_association.forms.famille import (
    FamilleAccueilUpdateForm,
    FamilleCreateForm,
    FamilleMainUpdateForm,
    FamilleSearchForm,
    IndisponibiliteForm,
    SelectFamilleForm,
    AccueilForm)
from gestion_association.models.animal import Animal, statuts_association
from gestion_association.models.famille import Famille, Indisponibilite, Accueil, StatutFamille, StatutAccueil
from gestion_association.models.person import Person


@login_required()
def create_famille(request, pk):
    title = "Créer une famille"
    personne = Person.objects.get(id=pk)
    if request.method == "POST":
        famille_form = FamilleCreateForm(data=request.POST)
        preference_form = PreferenceForm(data=request.POST)
        if famille_form.is_valid() and preference_form.is_valid():
            # Rattachement manuel de la personne et des préférences
            preference = preference_form.save()
            famille = famille_form.save(commit=False)
            famille.preference = preference
            famille.personne = personne
            famille.save()
            # La personne devient FA
            personne.is_famille = True
            personne.save()
            return redirect("detail_famille", pk=famille.id)
    else:
        famille_form = FamilleCreateForm()
        preference_form = PreferenceForm()
    return render(request, "gestion_association/famille/famille_create_form.html", locals())


@login_required
def famille_list(request):
    title = "Liste des familles"
    selected = "familles"
    famille_list = Famille.objects.all()

    if request.method == "POST":
        form = FamilleSearchForm(request.POST)
        if form.is_valid():
            base_url = reverse('familles')
            query_string = form.data.urlencode()
            url = '{}?{}'.format(base_url, query_string)
            return redirect(url)
    else:
        form = FamilleSearchForm()
        nom_personne_form = request.GET.get("nom_personne", "")
        places_dispos_form = request.GET.get("places_dispos", "")
        quarantaine_form = request.GET.get("quarantaine", "")
        exterieur_form = request.GET.get("exterieur", "")
        statut_form = request.GET.get("statut", "")
        vide_form = request.GET.get("vide", "")
        date_presence_min = request.GET.get("date_presence_min", "")
        date_presence_max = request.GET.get("date_presence_max", "")
        date_indispo_min = request.GET.get("date_indispo_min", "")
        date_indispo_max = request.GET.get("date_indispo_max", "")
        a_deplacer = request.GET.get("a_deplacer", "")

        if nom_personne_form:
            famille_list = famille_list.filter(personne__nom__icontains=nom_personne_form)
            form.fields["nom_personne"].initial = nom_personne_form
        if statut_form:
            famille_list = famille_list.filter(statut=statut_form)
            form.fields["statut"].initial = statut_form
        if vide_form:
            form.fields["vide"].initial = vide_form
            if vide_form == 'NON':
                famille_list = famille_list.filter(animal__isnull=False)
            elif vide_form == 'OUI':
                famille_list = famille_list.filter(animal__isnull=True)
        if quarantaine_form:
            famille_list = famille_list.filter(preference__quarantaine=quarantaine_form)
            form.fields["quarantaine"].initial = quarantaine_form
        if exterieur_form:
            famille_list = famille_list.filter(preference__exterieur=exterieur_form)
            form.fields["exterieur"].initial = exterieur_form
        if places_dispos_form:
            famille_list = famille_list.annotate(nb_animaux=Count("animal"))\
                .filter(nb_places__gte=F("nb_animaux") + int(places_dispos_form))
            form.fields["places_dispos"].initial = places_dispos_form
        if date_presence_min:
            famille_list = famille_list.exclude(
                indisponibilite__date_debut__lte=date_presence_min,
                indisponibilite__date_fin__gte=date_presence_min,
            )
            form.fields["date_presence_min"].initial = date_presence_min
        if date_presence_max:
            famille_list = famille_list.exclude(
                indisponibilite__date_debut__lte=parse_date(date_presence_max),
                indisponibilite__date_fin__gte=parse_date(date_presence_max),
            )
            form.fields["date_presence_max"].initial = date_presence_max
        # Ces trois valeurs ne sont pas des champs du formulaire, uniquement
        # des parametres d'url remplis depuis la page d'accueil
        if date_indispo_min:
            famille_list = famille_list.filter(indisponibilite__date_debut__gte=parse_date(date_indispo_min))
        if date_indispo_max:
            famille_list = famille_list.filter(indisponibilite__date_debut__lte=parse_date(date_indispo_max))
        if a_deplacer:
            famille_list = famille_list.filter(accueil__statut=StatutAccueil.A_DEPLACER.name)


    # Pagination : 10 éléments par page
    paginator = Paginator(famille_list.order_by("-date_mise_a_jour"), 10)
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        famille_list = paginator.page(page)
    except EmptyPage:
        # Si on dépasse la limite de pages, on prend la dernière
        famille_list = paginator.page(paginator.num_pages())
    return render(request, "gestion_association/famille/famille_list.html", locals())


@login_required
def update_accueil(request, pk):
    accueil = Accueil.objects.get(id=pk)
    famille = accueil.famille
    title = "Mise à jour d'un accueil"

    if request.method == "POST":
        form = AccueilForm(request.POST, instance=accueil)
        if form.is_valid():
            # La sauvegarde de l'accueil gère toutes les conséquences éventuelles
            form.save()

            return redirect("detail_famille", pk=famille.id)
    else:
        form = AccueilForm(instance=accueil)

    return render(request, "gestion_association/famille/accueil_update_form.html", locals())

@login_required
def end_accueil(request, pk):
    accueil = Accueil.objects.get(id=pk)
    accueil.date_fin = timezone.now().date()
    # La sauvegarde de l'accueil gère toutes les conséquences de la fin d'accueil
    accueil.save()
    return redirect("detail_famille", pk=accueil.famille.id)

@login_required
def famille_select_for_animal(request, pk):

    animal = Animal.objects.get(id=pk)
    title = "Trouver une famille pour " + animal.nom

    data = request.POST.get("famille")

    form = SelectFamilleForm(request.POST)
    if animal.get_animaux_lies():
        animals_queryset = animal.get_animaux_lies() | Animal.objects.filter(id=pk)
    else :
        animals_queryset = Animal.objects.filter(id=pk)
    form.fields["animaux"].queryset = animals_queryset
    form.fields["famille"].queryset = Famille.objects.exclude(statut="INACTIVE")
    animals = animals_queryset.all()

    if request.method == "POST":
        if form.is_valid():
            # On crée un accueil par animal pour faciliter la gestion des accueils
            famille = form.cleaned_data["famille"]
            date_debut = form.cleaned_data["date_debut"]
            for animal_fa in form.cleaned_data["animaux"].all():
                accueil = Accueil.objects.create(animal=animal_fa, famille=famille, date_debut=date_debut)
                accueil.save()
                animal_fa.famille = famille
                animal_fa.save()
            # La famille est maintenant occupée
            famille.statut = StatutFamille.OCCUPE.name

            return redirect("detail_animal", pk=animal.id)

    return render(request, "gestion_association/famille/famille_select_form.html", locals())


class FamilleUpdateMainForm(object):
    pass


@login_required()
def update_accueil_famille(request, pk):
    title = "Modifier une famille"
    famille = Famille.objects.get(id=pk)
    if request.method == "POST":
        famille_form = FamilleAccueilUpdateForm(data=request.POST, instance=famille)
        preference_form = PreferenceForm(data=request.POST, instance=famille.preference)
        if famille_form.is_valid() and preference_form.is_valid():
            preference = preference_form.save()
            famille = famille_form.save()
            return redirect("detail_famille", pk=famille.id)
    else:
        famille_form = FamilleAccueilUpdateForm(instance=famille)
        preference_form = PreferenceForm(instance=famille.preference)
    return render(request, "gestion_association/famille/famille_accueil_form.html", locals())


class UpdateMainFamille(LoginRequiredMixin, UpdateView):
    model = Famille
    form_class = FamilleMainUpdateForm
    template_name = "gestion_association/famille/famille_main_form.html"

    def get_success_url(self):
        return reverse_lazy("detail_famille", kwargs={"pk": self.object.id})

    def get_context_data(self, **kwargs):
        context = super(UpdateMainFamille, self).get_context_data(**kwargs)
        context['title'] = "Modification de la FA de   " + str(self.object.personne)
        return context


@login_required()
def create_indisponibilite(request, pk):
    title = "Ajout d'une indisponibilité"
    famille = Famille.objects.get(id=pk)
    if request.method == "POST":
        form = IndisponibiliteForm(data=request.POST)
        if form.is_valid():
            # Rattachement manuel de la famille
            indisponibilite = form.save(commit=False)
            indisponibilite.famille = famille
            indisponibilite.save()
            return redirect("detail_famille", pk=famille.id)
    else:
        form = IndisponibiliteForm()
    return render(request, "gestion_association/famille/indisponibilite_form.html", locals())


@login_required()
def delete_indisponibilite(request, pk):
    indispo = Indisponibilite.objects.get(id=pk)
    famille = indispo.famille
    indispo.delete()
    return redirect("detail_famille", pk=famille.id)


class UpdateIndisponibilite(LoginRequiredMixin, UpdateView):
    model = Indisponibilite
    form_class = IndisponibiliteForm
    template_name = "gestion_association/famille/indisponibilite_form.html"

    def get_success_url(self):
        return reverse_lazy("detail_famille", kwargs={"pk": self.object.famille.id})


def json_error_400(field, message):
    context = {"status": "400", "field": field, "reason": message}
    response = HttpResponse(json.dumps(context), content_type="application/json")
    response.status_code = 400
    return response


@method_decorator(csrf_exempt, name="dispatch")
class FamilleCandidateAPIView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        animal = Animal.objects.get(id=pk)
        animaux_candidats = [animal, *animal.animaux_lies.get_queryset().all()]
        try:
            data = json.loads(request.body)
        except ValueError:
            return json_error_400("body", "Invalid JSON request.")

        animaux_selectionnes = [a for a in animaux_candidats if a.pk in data.get("animaux", [])]
        date_debut = data.get("date_debut")

        if date_debut:
            try:
                date_debut = parse_date(date_debut)
            except ValueError:
                return json_error_400("date_debut", "Vous devez sélectionner une date valide.")

        else:
            return json_error_400("date_debut", "Vous devez sélectionner une date valide.")

        if not animaux_selectionnes:
            return json_error_400("animaux", "Vous devez sélectionner au moins un animal valide.")

        context = {
            "familles_candidates": [
                famille.to_json()
                for famille in Famille.objects.exclude(statut="INACTIVE")
                .exclude(
                    indisponibilite__date_debut__lte=date_debut,
                    indisponibilite__date_fin__gte=date_debut,
                )
                .annotate(nb_animaux=Count("animal"))
                .filter(nb_places__gte=F("nb_animaux") + len(animaux_selectionnes))
            ]
        }
        response = HttpResponse(json.dumps(context), content_type="application/json")
        response.status_code = 200
        return response


@login_required()
def select_animal_form(request, pk):
    itle = "Création d'un accueil"
    famille = Famille.objects.get(id=pk)
    if request.method == "POST":
        animal_form = AnimalSelectForFaForm(data=request.POST)
        accueil_form = AccueilForm(data=request.POST)

        if animal_form.is_valid() and accueil_form.is_valid():
            # Un accueil par animal
            date_debut = accueil_form.cleaned_data["date_debut"]
            date_fin = accueil_form.cleaned_data["date_fin"]
            commentaire = accueil_form.cleaned_data["commentaire"]
            for animal in animal_form.cleaned_data['animaux']:
                accueil = Accueil.objects.create(animal=animal, famille=famille, date_debut=date_debut,
                                                 date_fin=date_fin, commentaire=commentaire)
                accueil.famille = famille
                accueil.animal = animal
                accueil.save()
            famille.statut = StatutFamille.OCCUPE.name
            return redirect("detail_famille", pk=famille.id)
    else:
        animal_form = AnimalSelectForFaForm()
        accueil_form = AccueilForm()
    return render(request, "gestion_association/famille/famille_select_animal_form.html", locals())