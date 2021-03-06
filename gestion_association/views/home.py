import sys
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone

from gestion_association.models import OuiNonChoice
from gestion_association.models.adoption import TarifAdoption, TarifBonSterilisation, Adoption, BonSterilisation, \
    OuiNonVisiteChoice
from gestion_association.models.animal import Animal, statuts_association
from gestion_association.models.famille import Famille, StatutAccueil, Accueil

@login_required
def index(request):
    selected = "accueil"
    title = "Tableau de bord"

    today = timezone.now().date()
    interval_10 = today + timedelta(days=10)
    interval_5_weeks_ago = today - timedelta(days=35)
    # Valeurs str utilisées dans le template html
    today_str = today.strftime("%Y-%m-%d")
    interval_10_str = interval_10.strftime("%Y-%m-%d")
    interval_5_weeks_ago_str = interval_5_weeks_ago.strftime("%Y-%m-%d")

    statuts_association_filter = ""
    for statut in statuts_association:
        statuts_association_filter += 'statuts='
        statuts_association_filter += statut
        statuts_association_filter += '&'
    # Partie adoptions
    # A proposer à l'adoption
    a_proposer = Animal.objects.filter(statut='ADOPTABLE').count()
    #A l'adoption
    a_l_adoption = Animal.objects.filter(statut='A_ADOPTER').count()
    # Acomptes
    acomptes = Adoption.objects.filter(acompte_verse=OuiNonChoice.NON.name).count()
    # Adoptions pré-visites
    adoption_previsite = Adoption.objects.filter(animal__statut='ADOPTION') \
        .filter(pre_visite=OuiNonChoice.NON.name).filter(acompte_verse=OuiNonChoice.OUI.name).count()
    # Adoptions en attente de paiement complet
    adoption_paiement = Adoption.objects.filter(animal__statut='ADOPTION').filter(pre_visite=OuiNonChoice.OUI.name) \
        .filter(acompte_verse=OuiNonChoice.OUI.name).filter(montant_restant__gt = Decimal(0)).count()
    # Adoptions attendant leur visite de contrôle
    adoption_post = Adoption.objects.filter(visite_controle=OuiNonChoice.NON.name)\
        .filter(date__lte=interval_5_weeks_ago).count()
    # Post visite à contrôler
    adoption_controle = Adoption.objects.\
        filter(visite_controle__in=[OuiNonVisiteChoice.ALIMENTAIRE.name,OuiNonVisiteChoice.VACCIN.name])\
    .count()
    # Adoptions à clore
    adoption_over = Adoption.objects.filter(animal__statut='ADOPTE')\
        .filter(visite_controle=OuiNonChoice.OUI.name).count()


    # Partie soins
    # Animaux à stériliser
    sterilises = Animal.objects.filter(sterilise=OuiNonChoice.NON.name).filter(statut__in=statuts_association).count()
    # Animaux en soin
    soins = Animal.objects.filter(statut='SOIN').count()
    #Animaux à tester (fiv/felv)
    fiv_felv = Animal.objects.filter(statut__in=statuts_association).filter(Q(fiv='NT')|Q(felv='NT')).count()
    # Bon de stérilisation à envoyer
    bon_a_envoyer = BonSterilisation.objects.filter(envoye=OuiNonChoice.NON.name).count()
    # Bon de stérilisation arrivant à expiation (10 jours)
    bon_a_utilise = BonSterilisation.objects.filter(utilise=OuiNonChoice.NON.name).filter(date_max__gte=today)\
        .filter(date_max__lte=interval_10).count()
    # Vaccins à faire (10 jours)
    vaccins = Animal.objects.filter(statut__in=statuts_association).filter(date_prochain_vaccin__gte=today)\
        .filter(date_prochain_vaccin__lte=interval_10).count()

    # Partie FA
    # Animaux en FA
    en_famille = Animal.objects.filter(famille__isnull=False).count()
    # Familles disponibles
    disponibles = Famille.objects.filter(statut='DISPONIBLE').count()
    # Familles à visiter
    visites = Famille.objects.filter(statut='A_VISITER').count()
    # Animaux à placer
    a_placer = Animal.objects.filter(famille__isnull=True).filter(statut__in=statuts_association).count()
    # Animaux à déplacer sous 10 jours
    a_deplacer_10 = Famille.objects.filter(animal__isnull=False).filter(indisponibilite__date_debut__gte=today)\
        .filter(indisponibilite__date_debut__lte=interval_10).count()
    # Animaux à déplacer manuellement (accueils arrivant à terme)
    accueils_a_deplacer = Accueil.objects.filter(statut=StatutAccueil.A_DEPLACER.name).count()


    #Taux de remplissage
    familles_occupees =  Famille.objects.filter(animal__isnull=False).distinct().count()
    total_familles = Famille.objects.filter(statut__in=('DISPONIBLE','INDISPONIBLE','OCCUPE')).count()
    if total_familles > 1:
        taux_remplissage = int((familles_occupees/total_familles) * 100)

    return render(request, "gestion_association/home.html", locals())


@login_required
def parametrage(request):
    selected = "parametrage"
    tarifs_adoption = TarifAdoption.objects.all()
    tarifs_sterilisation = TarifBonSterilisation.objects.all()
    return render(request, "gestion_association/parametrage.html", locals())
