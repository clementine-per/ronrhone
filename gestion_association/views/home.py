from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from gestion_association.models.adoption import TarifAdoption, TarifBonSterilisation


@login_required
def index(request):
    selected = "accueil"
    title = "Tableau de bord"
    return render(request, "gestion_association/home.html", locals())

@login_required
def parametrage(request):
    selected = "parametrage"
    tarifs_adoption = TarifAdoption.objects.all()
    tarifs_sterilisation = TarifBonSterilisation.objects.all()
    return render(request, "gestion_association/parametrage.html", locals())