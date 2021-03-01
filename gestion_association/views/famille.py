from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from gestion_association.forms import PreferenceForm
from gestion_association.forms.animal import SelectFamilleForm
from gestion_association.forms.famille import FamilleCreateForm, FamilleSearchForm
from gestion_association.models.famille import Famille
from gestion_association.models.person import Person


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
            if nom_personne_form is not None:
                famille_list = famille_list.filter(personne__nom__icontains=nom_personne_form)
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
def famille_select(request):
    form = SelectFamilleForm()
    return render(request, "gestion_association/famille/famille_select_form.html", locals())