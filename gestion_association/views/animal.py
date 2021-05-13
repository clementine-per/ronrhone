
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage, Paginator
from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse
from django.utils.dateparse import parse_date
from django.db.models import Q
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
            base_url = reverse('animals')
            query_string = form.data.urlencode()
            url = '{}?{}'.format(base_url, query_string)
            return redirect(url)

    else:
        form = AnimalSearchForm()
        nom_form = request.GET.get("nom", "")
        identification_form = request.GET.get("identification", "")
        type_form = request.GET.get("type", "")
        sterilise_form = request.GET.get("sterilise", "")
        sans_fa_form = request.GET.get("sans_fa", "")
        statuts_form = request.GET.getlist("statuts","")
        date_naissance_min = request.GET.get("date_naissance_min", "")
        date_naissance_max = request.GET.get("date_naissance_max", "")
        date_prochain_vaccin_min = request.GET.get("date_prochain_vaccin_min", "")
        date_prochain_vaccin_max = request.GET.get("date_prochain_vaccin_max", "")
        date_vermifuge_min = request.GET.get("date_vermifuge_min", "")
        date_vermifuge_max = request.GET.get("date_vermifuge_max", "")
        fiv_felv_form = request.GET.get("fiv_felv", "")

        if nom_form:
            animals = animals.filter(nom__icontains=nom_form)
            form.fields["nom"].initial = nom_form
        if type_form:
            animals = animals.filter(type=type_form)
            form.fields["type"].initial = type_form
        if identification_form:
            animals = animals.filter(identification__icontains=identification_form)
            form.fields["identification"].initial = identification_form
        if sterilise_form:
            animals = animals.filter(sterilise=sterilise_form)
            form.fields["sterilise"].initial = sterilise_form
        if sans_fa_form:
            form.fields["sans_fa"].initial = sans_fa_form
            if sans_fa_form == OuiNonChoice.OUI.name:
                animals = animals.filter(famille__isnull=True)
            if sans_fa_form == OuiNonChoice.NON.name:
                animals = animals.filter(famille__isnull=False)
        if statuts_form:
            form.fields["statuts"].initial = statuts_form
            animals = animals.filter(statut__in=statuts_form)
        if date_naissance_min:
            form.fields["date_naissance_min"].initial = date_naissance_min
            animals = animals.filter(date_naissance__gte=parse_date(date_naissance_min))
        if date_naissance_max:
            form.fields["date_naissance_max"].initial = date_naissance_max
            animals = animals.filter(date_naissance__lte=parse_date(date_naissance_max))
        if date_prochain_vaccin_min:
            form.fields["date_prochain_vaccin_min"].initial = date_prochain_vaccin_min
            animals = animals.filter(date_prochain_vaccin__gte=parse_date(date_prochain_vaccin_min))
        if date_prochain_vaccin_max:
            form.fields["date_prochain_vaccin_max"].initial = date_prochain_vaccin_max
            animals = animals.filter(date_prochain_vaccin__lte=parse_date(date_prochain_vaccin_max))
        if fiv_felv_form:
            form.fields["fiv_felv"].initial = fiv_felv_form
            if fiv_felv_form == OuiNonChoice.OUI.name:
                animals = animals.filter(fiv=OuiNonChoice.OUI.name).filter(felv=OuiNonChoice.OUI.name)
            if fiv_felv_form == OuiNonChoice.NON.name:
                animals = animals.filter(Q(fiv='NT')|Q(felv='NT'))

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

@login_required()
def create_animal(request):
    title = "Créer une famille"
    if request.method == "POST":
        animal_form = AnimalCreateForm(data=request.POST)
        preference_form = PreferenceForm(data=request.POST)
        if animal_form.is_valid() and preference_form.is_valid():
            # Rattachement manuel de l'animal et des préférences
            preference = preference_form.save()
            animal = animal_form.save(commit=False)
            animal.preference = preference
            animal.save()
            return redirect("detail_animal", pk=animal.id)
    else:
        animal_form = AnimalCreateForm()
        preference_form = PreferenceForm()
    return render(request, "gestion_association/animal/animal_create_form.html", locals())


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
