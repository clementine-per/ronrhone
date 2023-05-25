from datetime import timedelta
from decimal import Decimal

from dateutil.relativedelta import relativedelta

from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Max, Q, Sum
from django.shortcuts import render
from django.utils import timezone

from gestion_association.models import OuiNonChoice
from gestion_association.models.adoption import (
    Adoption,
    BonSterilisation,
    OuiNonVisiteChoice,
    TarifAdoption,
    TarifBonSterilisation,
)
from gestion_association.models.animal import Animal, Parrainage, StatutAnimal, statuts_association
from gestion_association.models.famille import Accueil, Famille, StatutAccueil
from gestion_association.models.person import Adhesion, Person
from gestion_association.views.utils import admin_test

statuts_adoption = [
    StatutAnimal.A_ADOPTER.name,
    StatutAnimal.ADOPTION.name,
    StatutAnimal.ADOPTABLE.name,
    StatutAnimal.ADOPTE.name,
]

@login_required
def index(request):
    selected = "accueil"
    title = "Tableau de bord"

    today = timezone.now().date()
    interval_10 = today + timedelta(days=10)
    interval_10_ago = today - timedelta(days=10)
    interval_15_ago = today - timedelta(days=15)
    interval_5_weeks_ago = today - timedelta(days=35)
    interval_5_months_ago = today - relativedelta(months=5)
    interval_7_months_ago = today - relativedelta(months=7)
    # Valeurs str utilisées dans le template html
    today_str = today.strftime("%Y-%m-%d")
    interval_10_str = interval_10.strftime("%Y-%m-%d")
    interval_10_ago_str = interval_10_ago.strftime("%Y-%m-%d")
    interval_15_ago_str = interval_15_ago.strftime("%Y-%m-%d")
    interval_5_weeks_ago_str = interval_5_weeks_ago.strftime("%Y-%m-%d")
    interval_7_months_ago_str = interval_7_months_ago.strftime("%Y-%m-%d")
    interval_5_months_ago_str = interval_5_months_ago.strftime("%Y-%m-%d")

    statuts_association_filter = ""
    for statut in statuts_association:
        statuts_association_filter += "statuts="
        statuts_association_filter += statut
        statuts_association_filter += "&"
    # Partie adoptions
    # A proposer à l'adoption
    a_proposer = Animal.objects.filter(inactif=False).filter(statut="ADOPTABLE").count()
    # A l'adoption
    a_l_adoption = Animal.objects.filter(inactif=False).filter(statut="A_ADOPTER").count()
    # Acomptes
    acomptes = (
        Adoption.objects.filter(acompte_verse=OuiNonChoice.NON.name).filter(annule=False).count()
    )
    # Adoptions pré-visites
    adoption_previsite = (
        Adoption.objects.filter(animal__statut="ADOPTION")
        .filter(annule=False)
        .filter(pre_visite=OuiNonChoice.NON.name)
        .filter(acompte_verse=OuiNonChoice.OUI.name)
        .count()
    )
    # Adoptions en attente de paiement complet
    adoption_paiement_list = (
        Adoption.objects.filter(animal__statut="ADOPTION")
        .filter(pre_visite=OuiNonChoice.OUI.name)
        .filter(acompte_verse=OuiNonChoice.OUI.name)
        .filter(montant_restant__gt=Decimal(0))
        .filter(annule=False)
    )
    adoption_paiement_montant = adoption_paiement_list.aggregate(Sum("montant_restant"))
    adoption_paiement = adoption_paiement_list.count()
    # Adoptions attendant leur visite de contrôle
    adoption_post = (
        Adoption.objects.filter(visite_controle=OuiNonChoice.NON.name)
        .filter(animal__statut__in=statuts_adoption)
        .filter(annule=False)
        .filter(date_visite__lte=today)
        .filter(animal__sterilise=OuiNonChoice.OUI.name)
        .count()
    )
    # Post visite à contrôler
    adoption_controle = (
        Adoption.objects.filter(annule=False)
            .filter(animal__statut__in=statuts_adoption)
            .filter(
            visite_controle__in=[
                OuiNonVisiteChoice.ALIMENTAIRE.name,
                OuiNonVisiteChoice.VACCIN.name,
            ]
        )
        .count()
    )
    # Adoptions à clore
    adoption_over = (
        Adoption.objects.filter(animal__statut="ADOPTE")
        .filter(annule=False)
        .filter(visite_controle=OuiNonChoice.OUI.name)
        .count()
    )
    # Adoptions sans sterilisation
    adoption_ste = (
        Adoption.objects.filter(
            animal__statut__in=(
                StatutAnimal.ADOPTION.name,
                StatutAnimal.ADOPTE_DEFINITIF.name,
                StatutAnimal.ADOPTE.name,
            )
        )
        .filter(animal__sterilise=OuiNonChoice.NON.name)
        .filter(annule=False)
        .filter(animal__date_naissance__lte=interval_7_months_ago)
        .count()
    )

    # Partie Association
    # Parrainages
    parrainages = Parrainage.objects.filter(date_fin__gte=interval_10_ago).filter(
        date_fin__lte=interval_10
    )
    date_parrainage_10 = Person.objects.filter(parrainage__in=parrainages).count()
    # Adhésion arrivant à échéance (qui ont entre 11 et 12 mois)
    interval_11_months_ago = today - relativedelta(months=11)
    interval_12_months_ago = today - relativedelta(months=12)
    interval_11_months_ago_str = interval_11_months_ago.strftime("%Y-%m-%d")
    interval_12_months_ago_str = interval_12_months_ago.strftime("%Y-%m-%d")
    adhesions_a_renouveler = (
        Adhesion.objects.values("personne")
        .annotate(max_date=Max("date"))
        .filter(max_date__lte=interval_11_months_ago)
        .filter(max_date__gte=interval_12_months_ago)
        .count()
    )
    # Nouvelles parrain à donner
    interval_1_months_ago = today - relativedelta(months=1)
    interval_1_months_ago_str = interval_1_months_ago.strftime("%Y-%m-%d")
    nouvelles_parrain = (
        Parrainage.objects.filter(date_fin__gte=today)
        .filter(date_debut__lte=today)
        .filter(date_nouvelles__lte=interval_1_months_ago)
        .count()
    )

    # Partie soins
    # Animaux en soin
    soins = Animal.objects.filter(inactif=False).filter(statut="SOIN").count()
    # Animaux à stériliser
    a_steriliser = (
        Animal.objects.filter(inactif=False)
        .filter(statut__in=statuts_association)
        .filter(sterilise=OuiNonChoice.NON.name)
        .filter(date_naissance__lte=interval_5_months_ago)
        .count()
    )
    # Bon de stérilisation à envoyer
    bon_a_envoyer = (
        BonSterilisation.objects.filter(envoye=OuiNonChoice.NON.name)
        .filter(adoption__annule=False)
        .count()
    )
    # Bon de stérilisation arrivant à expiation (10 jours)
    bon_a_utilise = (
        BonSterilisation.objects.filter(utilise=OuiNonChoice.NON.name)
        .filter(date_max__gte=today)
        .filter(adoption__annule=False)
        .filter(date_max__lte=interval_10)
        .count()
    )
    # Vaccins à faire (10 jours)
    vaccins = (
        Animal.objects.filter(inactif=False)
        .filter(statut__in=statuts_association)
        .filter(date_prochain_vaccin__gte=today)
        .filter(date_prochain_vaccin__lte=interval_10)
        .count()
    )
    # Vaccins dépassés
    vaccins_retard = (
        Animal.objects.filter(inactif=False)
        .filter(statut__in=statuts_association)
        .filter(date_prochain_vaccin__lte=today)
        .count()
    )
    # Chatons en fin de sevrage
    interval_2_and_half_month_ago = today - relativedelta(months=2) - timedelta(days=15)
    interval_2_and_half_month_ago_str = interval_2_and_half_month_ago.strftime("%Y-%m-%d")
    fin_sevrage = (
        Animal.objects.filter(inactif=False)
        .filter(statut="SEVRAGE")
        .filter(date_naissance__lte=interval_2_and_half_month_ago)
        .count()
    )
    # Fin de quarantaine
    fin_quarantaine = (
        Animal.objects.filter(inactif=False)
        .filter(statut="QUARANTAINE")
        .filter(date_arrivee__lte=interval_15_ago)
        .count()
    )

    # Partie FA
    # Animaux en FA
    en_famille = (
        Animal.objects.filter(statut__in=statuts_association)
        .filter(inactif=False)
        .filter(famille__isnull=False)
        .count()
    )
    # Familles disponibles
    disponibles = (
        Famille.objects.filter(statut="DISPONIBLE")
        .exclude(
            indisponibilite__date_debut__lte=today,
            indisponibilite__date_fin__gte=today,
        )
        .count()
    )
    # Familles à nouveau disponibles
    disponibles_again = (
        Famille.objects.filter(statut="INDISPONIBLE")
        .exclude(
            indisponibilite__date_debut__lte=today,
            indisponibilite__date_fin__gte=today,
        )
        .count()
    )
    # Familles à visiter
    visites = Famille.objects.filter(statut="A_VISITER").count()
    # Animaux à placer
    a_placer = (
        Animal.objects.filter(inactif=False)
        .filter(famille__isnull=True)
        .filter(statut__in=statuts_association)
        .count()
    )
    # Animaux à déplacer sous 10 jours
    a_deplacer_10 = (
        Famille.objects.filter(animal__isnull=False)
        .filter(indisponibilite__date_debut__gte=today)
        .filter(indisponibilite__date_debut__lte=interval_10)
        .count()
    )
    # Animaux à déplacer manuellement (accueils arrivant à terme)
    accueils_a_deplacer = Accueil.objects.filter(statut=StatutAccueil.A_DEPLACER.name).count()
    # Animaux nekosable
    nekosables = (
        Animal.objects.filter(inactif=False)
        .filter(
            statut__in=(
                StatutAnimal.A_ADOPTER.name,
                StatutAnimal.QUARANTAINE.name,
                StatutAnimal.ADOPTABLE.name,
            )
        )
        .filter(nekosable=True)
        .exclude(famille__neko=True)
    )
    nb_nekosables = nekosables.count()
    # dont prêts = tous soins effectues
    nb_nekosables_prets = (
        nekosables.filter(sterilise=OuiNonChoice.OUI.name)
        .filter(vaccin_ok=OuiNonChoice.OUI.name)
        .filter(~Q(fiv="NT") & ~Q(felv="NT"))
        .exclude(identification__exact="")
        .count()
    )

    # Taux de remplissage
    places_disponibles = Famille.objects.filter(statut="DISPONIBLE").aggregate(Sum("nb_places"))
    if en_famille > 0:
        if places_disponibles["nb_places__sum"]:
            taux_remplissage = int(
                (en_famille / (en_famille + places_disponibles["nb_places__sum"])) * 100
            )
        else:
            taux_remplissage = 100

    return render(request, "gestion_association/home.html", locals())


@user_passes_test(admin_test)
def parametrage(request):
    context = {
        "selected": "parametrage",
        "tarifs_adoption": TarifAdoption.objects.all(),
        "tarifs_sterilisation": TarifBonSterilisation.objects.all(),
    }
    return render(request, "gestion_association/parametrage.html", context)
