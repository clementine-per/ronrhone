from dal import autocomplete

from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import EmptyPage, Paginator
from django.db.models import Max
from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse
from django.utils.dateparse import parse_date
from django.views.generic import CreateView, UpdateView

from gestion_association.forms.person import BenevoleForm, PersonForm, PersonSearchForm, AdhesionForm, \
    ParrainageSearchForm
from gestion_association.models.animal import Parrainage
from gestion_association.models.person import Person, Adhesion
from gestion_association.views.utils import admin_test, AdminTestMixin


class CreatePerson(AdminTestMixin, CreateView):
    model = Person
    form_class = PersonForm
    template_name = "gestion_association/person/person_form.html"

    def get_success_url(self):
        return reverse_lazy("detail_person", kwargs={"pk": self.object.id})

    def get_context_data(self, **kwargs):
        context = super(CreatePerson, self).get_context_data(**kwargs)
        context['title'] = "Créer une personne"
        return context


class UpdatePerson(AdminTestMixin, UpdateView):
    model = Person
    form_class = PersonForm
    template_name = "gestion_association/person/person_form.html"

    def get_success_url(self):
        return reverse_lazy("detail_person", kwargs={"pk": self.object.id})

    def get_context_data(self, **kwargs):
        context = super(UpdatePerson, self).get_context_data(**kwargs)
        context['title'] = f"Mettre à jour {str(self.object)}"
        return context


class BenevolePerson(AdminTestMixin, UpdateView):
    model = Person
    form_class = BenevoleForm
    template_name = "gestion_association/person/person_benevole_form.html"

    def get_success_url(self):
        return reverse_lazy("detail_person", kwargs={"pk": self.object.id})

    def form_valid(self, form):
        redirect_url = super(BenevolePerson, self).form_valid(form)
        self.object.is_benevole = True
        self.object.save()
        return redirect_url

    def get_context_data(self, **kwargs):
        context = super(BenevolePerson, self).get_context_data(**kwargs)
        context['title'] = f"Bénévole  {str(self.object)}"
        return context


class UpdateAdhesion(AdminTestMixin, UpdateView):
    model = Adhesion
    form_class = AdhesionForm
    template_name = "gestion_association/person/adhesion_form.html"

    def get_success_url(self):
        return reverse_lazy("detail_person", kwargs={"pk": self.object.personne.id})

    def get_context_data(self, **kwargs):
        context = super(UpdateAdhesion, self).get_context_data(**kwargs)
        context['title'] = "Mise à jour de l'adhésion"
        return context

@user_passes_test(admin_test)
def create_adhesion(request, pk):
    person = Person.objects.get(id=pk)
    title = f"Adhesion de {person.prenom} {person.nom}"
    if request.method == "POST":
        form = AdhesionForm(data=request.POST)
        if form.is_valid():
            adhesion = form.save(commit=False)
            adhesion.personne = person
            person.is_adherent = True
            adhesion.save()
            person.save()
            return redirect("detail_person", pk=person.id)

    else:
        form = AdhesionForm()

    return render(request, "gestion_association/person/adhesion_form.html", locals())


@user_passes_test(admin_test)
def person_list(request):
    title = "Liste des personnes"
    selected = "persons"
    person_list = Person.objects.all().filter(inactif=False)
    if request.method == "POST":
        form = PersonSearchForm(request.POST)
        if form.is_valid():
            base_url = reverse('persons')
            query_string = form.data.urlencode()
            url = f'{base_url}?{query_string}'
            return redirect(url)
    else:
        form = PersonSearchForm()
        nom_form = request.GET.get("nom", "")
        type_person_form = request.GET.get("type_person", "")
        date_parrainage_min = request.GET.get("date_parrainage_min", "")
        date_parrainage_max = request.GET.get("date_parrainage_max", "")
        date_adhesion_min = request.GET.get("date_adhesion_min", "")
        date_adhesion_max = request.GET.get("date_adhesion_max", "")
        if type_person_form:
            form.fields["type_person"].initial = type_person_form
            if type_person_form == "ADOPTANTE":
                person_list = person_list.filter(is_adoptante=True)
            if type_person_form == "ADHERENT":
                person_list = person_list.filter(is_adherent=True)
            if type_person_form == "PARRAIN":
                person_list = person_list.filter(is_parrain=True)
            if type_person_form == "ANCIEN_PROPRIO":
                person_list = person_list.filter(is_ancien_proprio=True)
            if type_person_form == "FA":
                person_list = person_list.filter(is_famille=True)
            if type_person_form == "BENEVOLE":
                person_list = person_list.filter(is_benevole=True)
        # Le filtre parrainage a toujours deux dates
        if date_parrainage_min and date_parrainage_max:
            parrainages = Parrainage.objects.filter(date_fin__gte=parse_date(date_parrainage_min))\
                .filter(date_fin__lte=parse_date(date_parrainage_max))
            person_list = person_list.filter(parrainage__in=parrainages)
    if nom_form:
            form.fields["nom"].initial = nom_form
            person_list = person_list.filter(nom__icontains=nom_form)
    if date_adhesion_min or date_adhesion_max:
        adhesions = Adhesion.objects.values('personne').annotate(max_date=Max('date'))
        if date_adhesion_min:
            form.fields["date_adhesion_min"].initial = date_adhesion_min
            adhesions = adhesions.filter(max_date__gte=date_adhesion_min)
        if date_adhesion_max:
            form.fields["date_adhesion_max"].initial = date_adhesion_max
            adhesions = adhesions.filter(max_date__lte=date_adhesion_max)
        adhesion_ids = [ad['personne'] for ad in adhesions.values('personne')]
        person_list = person_list.filter(pk__in=adhesion_ids)
    # Pagination : 10 éléments par page
    paginator = Paginator(person_list.order_by("-date_mise_a_jour"), 10)
    nb_results = person_list.count()
    try:
        page = request.GET.get("page") or 1
        persons = paginator.page(page)
    except EmptyPage:
        # Si on dépasse la limite de pages, on prend la dernière
        persons = paginator.page(paginator.num_pages())
    return render(request, "gestion_association/person/person_list.html", locals())


@user_passes_test(admin_test)
def person_benevole_cancel(request, pk):
    personne = Person.objects.get(id=pk)
    personne.is_benevole = False
    personne.commentaire_benevole = ""
    personne.save()
    return redirect("detail_person", pk=pk)


class PersonAutocomplete (autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Person.objects.none()

        qs = Person.objects.all()

        if self.q:
            qs = qs.filter(nom__istartswith=self.q)

        return qs

@user_passes_test(admin_test)
def parrainage_list(request):
    title = "Liste des parrainages"
    selected = "parrainages"
    parrainage_list = Parrainage.objects.all()
    if request.method == "POST":
        form = ParrainageSearchForm(request.POST)
        if form.is_valid():
            base_url = reverse('parrainages')
            query_string = form.data.urlencode()
            url = f'{base_url}?{query_string}'
            return redirect(url)
    else:
        form = ParrainageSearchForm()
        nom_personne = request.GET.get("nom_personne", "")
        nom_animal = request.GET.get("nom_animal", "")
        date_debut_min = request.GET.get("date_debut_min", "")
        date_debut_max = request.GET.get("date_debut_max", "")
        date_fin_min = request.GET.get("date_fin_min", "")
        date_fin_max = request.GET.get("date_fin_max", "")
        date_nouvelles_min = request.GET.get("date_nouvelles_min", "")
        date_nouvelles_max = request.GET.get("date_nouvelles_max", "")
    if nom_personne:
            form.fields["nom_personne"].initial = nom_personne
            parrainage_list = parrainage_list.filter(personne__nom__icontains=nom_personne)
    if nom_animal:
        form.fields["nom_animal"].initial = nom_animal
        parrainage_list = parrainage_list.filter(animal__nom__icontains=nom_animal)
    if date_debut_min:
        form.fields["date_debut_min"].initial = date_debut_min
        parrainage_list = parrainage_list.filter(date_debut__gte=parse_date(date_debut_min))
    if date_debut_max:
        form.fields["date_debut_max"].initial = date_debut_max
        parrainage_list = parrainage_list.filter(date_debut__lte=parse_date(date_debut_max))
    if date_fin_min:
        form.fields["date_fin_min"].initial = date_fin_min
        parrainage_list = parrainage_list.filter(date_fin__gte=parse_date(date_fin_min))
    if date_fin_max:
        form.fields["date_fin_max"].initial = date_fin_max
        parrainage_list = parrainage_list.filter(date_fin__lte=parse_date(date_fin_max))
    if date_nouvelles_min:
        form.fields["date_nouvelles_min"].initial = date_nouvelles_min
        parrainage_list = parrainage_list.filter(date_nouvelles__gte=parse_date(date_nouvelles_min))
    if date_nouvelles_max:
        form.fields["date_nouvelles_max"].initial = date_nouvelles_max
        parrainage_list = parrainage_list.filter(date_nouvelles__lte=parse_date(date_nouvelles_max))
    # Pagination : 10 éléments par page
    paginator = Paginator(parrainage_list, 10)
    nb_results = parrainage_list.count()
    try:
        page = request.GET.get("page") or 1
        parrainages = paginator.page(page)
    except EmptyPage:
        # Si on dépasse la limite de pages, on prend la dernière
        parrainages = paginator.page(paginator.num_pages())
    return render(request, "gestion_association/person/parrainage_list.html", locals())
