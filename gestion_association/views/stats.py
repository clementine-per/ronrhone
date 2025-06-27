import calendar
import locale

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from django.utils.timezone import datetime

from gestion_association.models.adoption import Adoption


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
        data_adoptions_current.append(adoptions.filter(date__year=date.year).filter(date__month=i).count())
        data_adoptions_past.append(adoptions.filter(date__year=date.year - 1).filter(date__month=i).count())
        i += 1

    # Partie Adoptions par durée
    labels_durees = ["Moins de 2 mois", "2 à 4 mois", "4 à 6 mois", "Plus de 6 mois"]
    # Adoptions pour l'année en cours
    data_adoptions_duree = []
    data_adoptions_duree.append(adoptions.filter(nb_jours__lt=60).count())
    data_adoptions_duree.append(adoptions.filter(nb_jours__gte=60).filter(nb_jours__lt=120).count())
    data_adoptions_duree.append(adoptions.filter(nb_jours__gte=120).filter(nb_jours__lt=180).count())
    data_adoptions_duree.append(adoptions.filter(nb_jours__gte=180).count())


    return render(request, "gestion_association/stats.html", locals())