import sys
from itertools import chain

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from gestion_association.forms import PreferenceForm
from gestion_association.forms.famille import FamilleCreateForm, FamilleSearchForm, FamilleMainUpdateForm, \
    FamilleAccueilUpdateForm, IndisponibiliteForm, SelectFamilleForm
from gestion_association.models.animal import Animal
from gestion_association.models.famille import Famille, Indisponibilite
from gestion_association.models.person import Person


@login_required()
def create_famille(request, pk):
    title = "Créer une famille"
    personne = Person.objects.get(id=pk)
    if request.method == "POST":
        famille_form = FamilleCreateForm(data=request.POST)
        preference_form = PreferenceForm(data=request.POST)
        if (famille_form.is_valid() and preference_form.is_valid()):
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
            nom_personne_form = form.cleaned_data["nom_personne"]
            places_dispos_form = form.cleaned_data["places_dispos"]
            quarantaine_form = form.cleaned_data["quarantaine"]
            exterieur_form = form.cleaned_data["exterieur"]
            statut_form = form.cleaned_data["statut"]
            date_presence_min = form.cleaned_data["date_presence_min"]
            date_presence_max = form.cleaned_data["date_presence_max"]
            if nom_personne_form:
                famille_list = famille_list.filter(personne__nom__icontains=nom_personne_form)
            if statut_form:
                famille_list = famille_list.filter(statut=statut_form)
            if quarantaine_form:
                famille_list = famille_list.filter(preference__quarantaine=quarantaine_form)
            if exterieur_form:
                famille_list = famille_list.filter(preference__exterieur=exterieur_form)
    else:
        form = FamilleSearchForm()
    # Pagination : 10 éléments par page
    paginator = Paginator(famille_list.order_by('-date_mise_a_jour'), 10)
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
def famille_select_for_animal(request, pk):

    animal = Animal.objects.get(id=pk)
    title = "Trouver une famille pour " + animal.nom

    data = request.POST.get("famille")

    form = SelectFamilleForm(request.POST)
    form.fields["animaux"].queryset = animal.animaux_lies.get_queryset() | Animal.objects.filter(id=pk)
    form.fields["famille"].queryset = Famille.objects.exclude(statut='INACTIVE')

    if request.method == "POST":
        print(request.POST["famille"])
        sys.stdout.flush()
        if form.is_valid():
            form.save()
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
        if (famille_form.is_valid() and preference_form.is_valid()):
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

@login_required()
def create_indisponibilite(request, pk):
    title = "Ajout d'une indisponibilité"
    famille = Famille.objects.get(id=pk)
    if request.method == "POST":
        form = IndisponibiliteForm(data=request.POST)
        if (form.is_valid()):
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

