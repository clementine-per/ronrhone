from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render

from gestion_association.models.adoption import TarifAdoption, TarifBonSterilisation, Adoption
from gestion_association.models.animal import Animal, statuts_association
from gestion_association.models.famille import Famille


@login_required
def index(request):
    selected = "accueil"
    title = "Tableau de bord"

    # Partie adoptions
    # Adoptions attendant leur visite de contrôle
    adoption_adoptes = Adoption.objects.filter(animal__statut='ADOPTE').filter(visite_controle='NON').count()
    # Adoptions à clore
    adoption_over = Adoption.objects.filter(animal__statut='ADOPTE').filter(visite_controle='OUI').count()
    # Adoptions pré-visites
    adoption_previsite = Adoption.objects.filter(animal__statut='ADOPTION').filter(pre_visite='NON').count()
    # Adoptions en cours
    adoption_en_cours = Adoption.objects.filter(animal__statut='ADOPTION').filter(pre_visite='OUI').count()
    #A l'adoption
    a_l_adoption = Animal.objects.filter(statut='A_ADOPTER').count()
    # A proposer à l'adoption
    a_proposer = Animal.objects.filter(statut='ADOPTABLE').count()

    # Partie soins
    # Animaux à stériliser
    sterilises = Animal.objects.filter(sterilise='NON').filter(statut__in=statuts_association).count()
    # Animaux en soin
    soins = Animal.objects.filter(statut='SOIN').count()
    #Animaux à tester (fiv/felv)
    fiv_felv = Animal.objects.filter(statut__in=statuts_association).filter(Q(fiv='NT')|Q(felv='NT')).count()

    # Partie FA
    # Animaux en FA
    en_famille = Animal.objects.filter(famille__isnull=False).count()
    # Familles disponibles
    disponibles = Famille.objects.filter(animal__isnull=True).filter(statut='DISPONIBLE').count()
    # Animaux à placer
    a_placer = Animal.objects.filter(famille__isnull=True).filter(statut__in=statuts_association).count()
    # Animaux à déplacer

    #Taux de remplissage
    familles_occupees =  Famille.objects.filter(animal__isnull=False).count()
    total_familles = Famille.objects.filter(statut='DISPONIBLE').count()
    if total_familles > 1:
        taux_remplissage = int((familles_occupees/total_familles) * 100)

    return render(request, "gestion_association/home.html", locals())


@login_required
def parametrage(request):
    selected = "parametrage"
    tarifs_adoption = TarifAdoption.objects.all()
    tarifs_sterilisation = TarifBonSterilisation.objects.all()
    return render(request, "gestion_association/parametrage.html", locals())
