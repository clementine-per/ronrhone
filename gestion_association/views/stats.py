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
    return render(request, "gestion_association/stats.html", locals())