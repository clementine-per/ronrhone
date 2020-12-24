import sys

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from gestion_association.forms.person import PersonForm, PersonSearchForm
from gestion_association.models.person import Person


class CreatePerson(LoginRequiredMixin, CreateView):
    model = Person
    form_class = PersonForm
    template_name = "gestion_association/person_form.html"

    def get_success_url(self):
        return reverse_lazy("person_list")

@login_required
def person_list(request):
    selected = "persons"
    person_list = Person.objects.all().filter(inactif=False)

    if request.method == "POST":
        form = PersonSearchForm(request.POST)
        if form.is_valid():

            nom_form = form.cleaned_data["nom"]
            type_person_form = form.cleaned_data["type_person"]
            if type_person_form is not None:
                if type_person_form == 'ADOPTANTE':
                    person_list = person_list.filter(is_adoptante=True)
                if type_person_form == 'FA':
                    person_list = person_list.filter(is_famille=True)
                if type_person_form == 'BENEVOLE':
                    person_list = person_list.filter(is_benevole=True)
            if nom_form is not None:
                person_list = person_list.filter(nom__icontains=nom_form)
    else:
        form = PersonSearchForm()
    # Pagination : 10 éléments par page
    paginator = Paginator(person_list.order_by('-date_mise_a_jour'), 10)
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        persons = paginator.page(page)
    except EmptyPage:
        # Si on dépasse la limite de pages, on prend la dernière
        persons = paginator.page(paginator.num_pages())
    return render(request, "gestion_association/person_list.html", locals())