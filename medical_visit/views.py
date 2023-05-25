from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import UpdateView

from gestion_association.views.utils import admin_test, AdminTestMixin
from medical_visit.forms import VisiteMedicaleSearchForm, VisiteMedicaleForm, TestResultsForm
from gestion_association.models.animal import Animal, TestResultChoice
from medical_visit.models import VisiteMedicale


@user_passes_test(admin_test)
def visite_medicale_list(request):
    title = "Liste des visites véterinaires"
    selected = "visites"
    visite_list = VisiteMedicale.objects.all()
    if request.method == "POST":
        form = VisiteMedicaleSearchForm(request.POST)
        if form.is_valid():
            base_url = reverse('visites')
            query_string = form.data.urlencode()
            url = f'{base_url}?{query_string}'
            return redirect(url)
    else:
        form = VisiteMedicaleSearchForm()
        veterinary_form = request.GET.get("veterinary", "")
        visit_type_form = request.GET.get("visit_type", "")
        date_min_form = request.GET.get("date_min", "")
        date_max_form = request.GET.get("date_max", "")
        if visit_type_form:
            form.fields["visit_type"].initial = visit_type_form
            visite_list = visite_list.filter(visit_type = visit_type_form)
        if veterinary_form:
            form.fields["veterinary"].initial = veterinary_form
            visite_list = visite_list.filter(veterinary__icontains=veterinary_form)
        if date_min_form:
            form.fields["date_min"].initial = date_min_form
            visite_list = visite_list.filter(date__gte=date_min_form)
        if date_max_form:
            form.fields["date_max"].initial = date_max_form
            visite_list = visite_list.filter(date__lte=date_max_form)
    # Pagination : 10 elements per page
    paginator = Paginator(visite_list.order_by("-date"), 10)
    nb_results = visite_list.count()
    total_amount = visite_list.aggregate(montant_total=Sum('amount'))
    try:
        page = request.GET.get("page") or 1
        visites = paginator.page(page)
    except EmptyPage:
        visites = paginator.page(paginator.num_pages())
    return render(request, "medical_visit/medical_visit_list.html", locals())


@user_passes_test(admin_test)
def create_visite_medicale(request):
    title = "Renseigner une visite vétérinaire"
    if request.method == "POST":
        processed = process_form_data(request.POST)

        if processed:

            return redirect("visites")

    else:
        visite_form = VisiteMedicaleForm()
        tests_form = TestResultsForm()

    return render(request, "medical_visit/medical_visit_create_form.html", locals())


class UpdateVisiteMedicale(AdminTestMixin, UpdateView):
    model = VisiteMedicale
    form_class = VisiteMedicaleForm
    template_name = "medical_visit/medical_visit_form.html"

    def get_success_url(self):
        return reverse_lazy("visites")

    def get_context_data(self, **kwargs):
        context = super(UpdateVisiteMedicale, self).get_context_data(**kwargs)
        context['title'] = f"Mettre à jour {str(self.object)}"
        return context


@user_passes_test(admin_test)
def create_visite_from_animal(request, pk):
    animal = Animal.objects.get(id=pk)
    title = f"Visite véterinaire pour {animal.nom}"
    if request.method == "POST":
        processed = process_form_data(request.POST)
        if processed:
            return redirect("detail_animal", pk=animal.id)

    else:
        visite_form = VisiteMedicaleForm()
        tests_form = TestResultsForm()
        if animal.get_animaux_lies():
            animals_queryset = animal.get_animaux_lies() | Animal.objects.filter(id=pk)
        else:
            animals_queryset = Animal.objects.filter(id=pk)
        visite_form.fields["animals"].queryset = animals_queryset
        visite_form.fields["animals"].initial = animal

    return render(request, "medical_visit/medical_visit_create_form.html", locals())


@user_passes_test(admin_test)
def delete_visite(request, pk):
    visite = VisiteMedicale.objects.get(id=pk)
    visite.delete()
    return redirect("visites")


def process_form_data(data):
    visite_form = VisiteMedicaleForm(data=data)
    tests_form = TestResultsForm(data=data)
    if visite_form.is_valid():
        visite = visite_form.save()
        if (
                tests_form.is_valid()
                and tests_form.cleaned_data['fiv'] != TestResultChoice.NT.name
                and tests_form.cleaned_data['felv'] != TestResultChoice.NT.name
        ):
            for animal in visite.animals.all():
                animal.fiv = tests_form.cleaned_data['fiv']
                animal.felv = tests_form.cleaned_data['felv']
                animal.save()
        return True
    return False