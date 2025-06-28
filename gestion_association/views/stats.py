import calendar
import locale

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from django.utils.timezone import datetime

from gestion_association.forms.stats import DureeAdoptionStatsForm
from gestion_association.models.adoption import Adoption
from django.db.models import F, IntegerField, ExpressionWrapper, Avg
from django.db.models.functions import ExtractYear, ExtractMonth


@login_required
def index(request):
    # Partie Adoptions
    labels_mois = []
    # Adoptions pour l'année en cours
    data_adoptions_current = []
    # Adoptions pour l'année précédente
    data_adoptions_past = []

    adoptions = Adoption.objects.all()
    # Pour que les mois soient en français
    locale.setlocale(locale.LC_ALL, 'fr_FR')
    date = datetime.now()

    i = 1
    current = date.year
    past = date.year - 1

    while (i < 13):
        labels_mois.append(calendar.month_name[i])
        data_adoptions_current.append(adoptions.filter(date__year=current).filter(date__month=i).count())
        data_adoptions_past.append(adoptions.filter(date__year=past).filter(date__month=i).count())
        i += 1

    # Prise en compte des filtres utilisateurs éventuels
    if request.method == "POST":
        adoption_duree_form = DureeAdoptionStatsForm(request.POST)
        if adoption_duree_form.is_valid():
            annee = adoption_duree_form.cleaned_data.get("annee")
            age = adoption_duree_form.cleaned_data.get("age")
            if annee:
                adoptions = adoptions.filter(date__year=annee)
            if age:
                adoptions = adoptions.annotate(start_year=ExtractYear('animal__date_naissance'),
                                   start_month=ExtractMonth('animal__date_naissance'),
                                   end_year=ExtractYear('date'),
                                   end_month=ExtractMonth('date'),
                ).annotate(
                    month_diff=ExpressionWrapper(
                        (F('end_year') - F('start_year')) * 12 + (F('end_month') - F('start_month')),
                        output_field=IntegerField()
                    )
                )
                if age == "CHATON":
                    adoptions = adoptions.filter(month_diff__lt=6)
                elif age == "ADULTE":
                    adoptions = adoptions.filter(month_diff__gte=6).filter(month_diff__lt=96)
                elif age == "SENIOR":
                    adoptions = adoptions.filter(month_diff__gte=96)

    else:
        adoption_duree_form = DureeAdoptionStatsForm()


    # Partie Adoptions par durée
    labels_durees = ["Moins de 2 mois", "2 à 4 mois", "4 à 6 mois", "Plus de 6 mois"]
    # Adoptions pour l'année en cours
    data_adoptions_duree = []
    data_adoptions_duree.append(adoptions.filter(nb_jours__lt=60).count())
    data_adoptions_duree.append(adoptions.filter(nb_jours__gte=60).filter(nb_jours__lt=120).count())
    data_adoptions_duree.append(adoptions.filter(nb_jours__gte=120).filter(nb_jours__lt=180).count())
    data_adoptions_duree.append(adoptions.filter(nb_jours__gte=180).count())

    moyenne = adoptions.aggregate(moyenne=Avg('nb_jours'))
    total_adoptions = adoptions.count()


    return render(request, "gestion_association/stats.html", locals())