from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView

from gestion_association.forms.visite_medicale import VisiteMedicaleSearchForm, VisiteMedicaleForm
from gestion_association.models.animal import Animal
from gestion_association.models.visite_medicale import VisiteMedicale


@login_required
def visite_medicale_list(request):
    title = "Liste des visites véterinaires"
    selected = "visites"
    visite_list = VisiteMedicale.objects.all()
    if request.method == "POST":
        form = VisiteMedicaleSearchForm(request.POST)
        if form.is_valid():
            base_url = reverse('visites')
            query_string = form.data.urlencode()
            url = '{}?{}'.format(base_url, query_string)
            return redirect(url)
    else:
        form = VisiteMedicaleSearchForm()
        veterinaire_form = request.GET.get("veterinaire", "")
        type_visite_form = request.GET.get("type_visite", "")
        date_min_form = request.GET.get("date_min", "")
        date_max_form = request.GET.get("date_max", "")
        if type_visite_form:
            form.fields["type_visite"].initial = type_visite_form
            visite_list = visite_list.filter(type_visite = type_visite_form)
        if veterinaire_form:
            form.fields["veterinaire"].initial = veterinaire_form
            visite_list = visite_list.filter(veterinaire__icontains=veterinaire_form)
        if date_min_form:
            form.fields["date_min"].initial = date_min_form
            visite_list = visite_list.filter(date__gte=date_min_form)
        if date_max_form:
            form.fields["date_max"].initial = date_max_form
            visite_list = visite_list.filter(date__lte=date_max_form)
    # Pagination : 10 éléments par page
    paginator = Paginator(visite_list.order_by("-date"), 10)
    nb_results = visite_list.count()
    montant_total = visite_list.aggregate(montant_total=Sum('montant'))
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        visites = paginator.page(page)
    except EmptyPage:
        # Si on dépasse la limite de pages, on prend la dernière
        visites = paginator.page(paginator.num_pages())
    return render(request, "gestion_association/visite_medicale/visite_medicale_list.html", locals())


class CreateVisiteMedicale(LoginRequiredMixin, CreateView):
    model = VisiteMedicale
    form_class = VisiteMedicaleForm
    template_name = "gestion_association/visite_medicale/visite_medicale_form.html"

    def get_success_url(self):
        return reverse_lazy("visites")

    def get_context_data(self, **kwargs):
        context = super(CreateVisiteMedicale, self).get_context_data(**kwargs)
        context['title'] = "Renseigner une visite vétérinaire"
        return context


class UpdateVisiteMedicale(LoginRequiredMixin, UpdateView):
    model = VisiteMedicale
    form_class = VisiteMedicaleForm
    template_name = "gestion_association/visite_medicale/visite_medicale_form.html"

    def get_success_url(self):
        return reverse_lazy("visites")

    def get_context_data(self, **kwargs):
        context = super(UpdateVisiteMedicale, self).get_context_data(**kwargs)
        context['title'] = "Mettre à jour " + str(self.object)
        return context

@login_required
def create_visite_from_animal(request, pk):
    animal = Animal.objects.get(id=pk)
    title = "Visite véterinaire pour " + animal.nom
    if request.method == "POST":
        form = VisiteMedicaleForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect("detail_animal", pk=animal.id)

    else:
        form = VisiteMedicaleForm()
        form.fields["animaux"].initial = animal

    return render(request, "gestion_association/visite_medicale/visite_medicale_form.html", locals())