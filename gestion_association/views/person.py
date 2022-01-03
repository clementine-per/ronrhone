from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage, Paginator
from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView

from gestion_association.forms.person import BenevoleForm, PersonForm, PersonSearchForm, AdhesionForm
from gestion_association.models.person import Person, Adhesion


class CreatePerson(LoginRequiredMixin, CreateView):
    model = Person
    form_class = PersonForm
    template_name = "gestion_association/person/person_form.html"

    def get_success_url(self):
        return reverse_lazy("detail_person", kwargs={"pk": self.object.id})

    def get_context_data(self, **kwargs):
        context = super(CreatePerson, self).get_context_data(**kwargs)
        context['title'] = "Créer une personne"
        return context


class UpdatePerson(LoginRequiredMixin, UpdateView):
    model = Person
    form_class = PersonForm
    template_name = "gestion_association/person/person_form.html"

    def get_success_url(self):
        return reverse_lazy("detail_person", kwargs={"pk": self.object.id})

    def get_context_data(self, **kwargs):
        context = super(UpdatePerson, self).get_context_data(**kwargs)
        context['title'] = "Mettre à jour " + str(self.object)
        return context


class BenevolePerson(LoginRequiredMixin, UpdateView):
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
        context['title'] = "Bénévole  " + str(self.object)
        return context


class UpdateAdhesion(LoginRequiredMixin, UpdateView):
    model = Adhesion
    form_class = AdhesionForm
    template_name = "gestion_association/person/adhesion_form.html"

    def get_success_url(self):
        return reverse_lazy("detail_person", kwargs={"pk": self.object.personne.id})

    def get_context_data(self, **kwargs):
        context = super(UpdateAdhesion, self).get_context_data(**kwargs)
        context['title'] = "Mise à jour de l'adhésion"
        return context

@login_required
def create_adhesion(request, pk):
    person = Person.objects.get(id=pk)
    title = "Adhesion de " + person.prenom + " " + person.nom
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


@login_required
def person_list(request):
    title = "Liste des personnes"
    selected = "persons"
    person_list = Person.objects.all().filter(inactif=False)
    if request.method == "POST":
        form = PersonSearchForm(request.POST)
        if form.is_valid():
            base_url = reverse('persons')
            query_string = form.data.urlencode()
            url = '{}?{}'.format(base_url, query_string)
            return redirect(url)
    else:
        form = PersonSearchForm()
        nom_form = request.GET.get("nom", "")
        type_person_form = request.GET.get("type_person", "")
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
        if nom_form:
            form.fields["nom"].initial = nom_form
            person_list = person_list.filter(nom__icontains=nom_form)
    # Pagination : 10 éléments par page
    paginator = Paginator(person_list.order_by("-date_mise_a_jour"), 10)
    nb_results = person_list.count()
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        persons = paginator.page(page)
    except EmptyPage:
        # Si on dépasse la limite de pages, on prend la dernière
        persons = paginator.page(paginator.num_pages())
    return render(request, "gestion_association/person/person_list.html", locals())


@login_required
def person_benevole_cancel(request, pk):
    personne = Person.objects.get(id=pk)
    personne.is_benevole = False
    personne.commentaire_benevole = ""
    personne.save()
    return redirect("detail_person", pk=pk)
