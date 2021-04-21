from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage, Paginator
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from gestion_association.forms import PreferenceForm
from gestion_association.forms.animal import (
    AnimalCreateForm,
    AnimalInfoUpdateForm,
    AnimalLinkedForm,
    AnimalSanteUpdateForm,
    AnimalSearchForm,
)
from gestion_association.models import OuiNonChoice
from gestion_association.models.animal import Animal


@login_required()
def search_animal(request):
    animals = Animal.objects.all()
    selected = "animals"
    title = "Liste des animaux"

    if request.method == "POST":
        form = AnimalSearchForm(request.POST)
        if form.is_valid():
            nom_form = form.cleaned_data["nom"]
            identification_form = form.cleaned_data["identification"]
            type_form = form.cleaned_data["type"]
            sterilise_form = form.cleaned_data["sterilise"]
            sans_fa_form = form.cleaned_data["sans_fa"]
            statuts_form = form.cleaned_data["statuts"]
            date_naissance_min = form.cleaned_data["date_naissance_min"]
            date_naissance_max = form.cleaned_data["date_naissance_max"]
            date_prochaine_visite_min = form.cleaned_data["date_prochaine_visite_min"]
            date_prochaine_visite_max = form.cleaned_data["date_prochaine_visite_max"]
            date_vermifuge_min = form.cleaned_data["date_vermifuge_min"]
            date_vermifuge_max = form.cleaned_data["date_vermifuge_max"]

            if nom_form:
                animals = animals.filter(nom__icontains=nom_form)
            if type_form:
                animals = animals.filter(type=type_form)
            if identification_form:
                animals = animals.filter(identification__icontains=identification_form)
            if sterilise_form:
                animals = animals.filter(sterilise=sterilise_form)
            if sans_fa_form and sans_fa_form == OuiNonChoice.OUI.name:
                animals = animals.filter(famille__isnull=True)
            if sans_fa_form and sans_fa_form == OuiNonChoice.NON.name:
                animals = animals.filter(famille__isnull=False)
            if statuts_form:
                animals = animals.filter(statut__in=statuts_form)
            if date_naissance_min:
                animals = animals.filter(date_naissance__gte=date_naissance_min)
            if date_naissance_max:
                animals = animals.filter(date_naissance__lte=date_naissance_max)
            if date_prochaine_visite_min:
                animals = animals.filter(date_prochain_vaccin__gte=date_prochaine_visite_min)
            if date_prochaine_visite_max:
                animals = animals.filter(date_prochain_vaccin__lte=date_prochaine_visite_max)

    else:
        form = AnimalSearchForm()
        # Le champ statut est initialisé, il faut appliquer le filtre dessus
        statuts_form = form["statuts"].value()
        animals = animals.filter(statut__in=statuts_form)

    # Pagination : 20 éléments par page
    paginator = Paginator(animals.order_by("-date_mise_a_jour"), 20)
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        animal_list = paginator.page(page)
    except EmptyPage:
        # Si on dépasse la limite de pages, on prend la dernière
        animal_list = paginator.page(paginator.num_pages())

    return render(request, "gestion_association/animal/animal_list.html", locals())


class CreateAnimal(LoginRequiredMixin, CreateView):
    model = Animal
    form_class = AnimalCreateForm
    template_name = "gestion_association/animal/animal_create_form.html"

    def get_success_url(self):
        return reverse_lazy("detail_animal", kwargs={"pk": self.object.id})

    def get_context_data(self, **kwargs):
        context = super(CreateAnimal, self).get_context_data(**kwargs)
        context['title'] = "Créer un animal"
        return context


@login_required()
def update_preference(request, pk):
    animal = Animal.objects.get(id=pk)
    title = "Modification des préférences de " + animal.nom
    if request.method == "POST":
        preference_form = PreferenceForm(data=request.POST, instance=animal.preference)
        animal_linked_form = AnimalLinkedForm(data=request.POST, instance=animal)
        if preference_form.is_valid() and animal_linked_form.is_valid():
            preference_form.save()
            animal_linked_form.save()
            return redirect("detail_animal", pk=pk)
    else:
        preference_form = PreferenceForm(instance=animal.preference)
        animal_linked_form = AnimalLinkedForm(instance=animal)
    return render(request, "gestion_association/animal/preference_form.html", locals())


class UpdateInformation(LoginRequiredMixin, UpdateView):
    model = Animal
    template_name = "gestion_association/animal/information_form.html"
    form_class = AnimalInfoUpdateForm

    def get_success_url(self):
        return reverse_lazy("detail_animal", kwargs={"pk": self.object.id})


class UpdateSante(LoginRequiredMixin, UpdateView):
    model = Animal
    template_name = "gestion_association/animal/sante_form.html"
    form_class = AnimalSanteUpdateForm

    def get_success_url(self):
        return reverse_lazy("detail_animal", kwargs={"pk": self.object.id})
