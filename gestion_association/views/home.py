from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from gestion_association.models.adoption import TarifAdoption, TarifBonSterilisation, Adoption
from gestion_association.models.animal import Animal


@login_required
def index(request):
    selected = "accueil"
    title = "Tableau de bord"
    # Adoptions attendant leur visite de contrôle
    adoption_adoptes = Adoption.objects.filter(animal__statut='ADOPTE').filter(visite_controle='NON').count()
    # Adoptions à clore
    adoption_over = Adoption.objects.filter(animal__statut='ADOPTE').filter(visite_controle='OUI').count()
    # Adoptions pré-visites
    adoption_previsite = Adoption.objects.filter(animal__statut='ADOPTION').filter(pre_visite='NON').count()
    # Adoptions en cours
    adoption_en_cours = Adoption.objects.filter(animal__statut='ADOPTION').filter(pre_visite='OUI').count()
    return render(request, "gestion_association/home.html", locals())


@login_required
def parametrage(request):
    selected = "parametrage"
    tarifs_adoption = TarifAdoption.objects.all()
    tarifs_sterilisation = TarifBonSterilisation.objects.all()
    return render(request, "gestion_association/parametrage.html", locals())
