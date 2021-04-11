import sys

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from gestion_association.forms.person import PersonForm, PersonSearchForm, BenevoleForm
from gestion_association.models.person import Person


class CreatePerson(LoginRequiredMixin, CreateView):
    model = Person
    form_class = PersonForm
    template_name = "gestion_association/person/person_form.html"

    def get_success_url(self):
        return reverse_lazy("detail_person", kwargs={"pk": self.object.id})


class UpdatePerson(LoginRequiredMixin, UpdateView):
    model = Person
    form_class = PersonForm
    template_name = "gestion_association/person/person_form.html"

    def get_success_url(self):
        return reverse_lazy("detail_person", kwargs={"pk": self.object.id})


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


@login_required
def person_list(request):
    title = "Liste des personnes"
    selected = "persons"
    person_list = Person.objects.all().filter(inactif=False)
    if request.method == "POST":
        form = PersonSearchForm(request.POST)
        if form.is_valid():
            nom_form = form.cleaned_data["nom"]
            type_person_form = form.cleaned_data["type_person"]
            if type_person_form is not None:
                if type_person_form == "ADOPTANTE":
                    person_list = person_list.filter(is_adoptante=True)
                if type_person_form == "FA":
                    person_list = person_list.filter(is_famille=True)
                if type_person_form == "BENEVOLE":
                    person_list = person_list.filter(is_benevole=True)
            if nom_form is not None:
                person_list = person_list.filter(nom__icontains=nom_form)
    else:
        form = PersonSearchForm()
    # Pagination : 10 éléments par page
    paginator = Paginator(person_list.order_by("-date_mise_a_jour"), 10)
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
