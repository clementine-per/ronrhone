import calendar
import locale

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from django.utils.timezone import datetime

from gestion_association.forms.stats import AnneeChoice, AnneeStatsForm, DureeAdoptionStatsForm
from gestion_association.models.adoption import Adoption
from django.db.models import F, IntegerField, ExpressionWrapper, Avg, Sum, Q, Count, DecimalField
from django.db.models.functions import ExtractYear, ExtractMonth

from gestion_association.models.animal import Animal
from medical_visit.models import VisiteMedicale


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

    # Prise en compte des filtres utilisateurs éventuels pour duree d'adoption
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

    # Partie données financières
    visites = VisiteMedicale.objects.all()

    adoptions_finance = Adoption.objects.filter(annule=False).exclude(montant=None)
    # Récupération de l'année saisie par l'utilisateur
    annee = None
    if request.method == "POST":
        annee_form = AnneeStatsForm(request.POST)
        if annee_form.is_valid():
            annee = annee_form.cleaned_data.get("annee")
            if annee:
                adoptions_finance = adoptions_finance.filter(date__year=annee)
                visites = visites.filter(date__year=annee)
    else:
        annee_form = AnneeStatsForm()
    # Calcul du montant total des visites médicales
    montant_total_visites = visites.aggregate(montant_total=Sum('amount'))['montant_total'] or 0
    # Calcul du montant total des adoptions
    montant_total_adoptions = adoptions_finance.aggregate(montant_total=Sum('montant'))['montant_total'] or 0
    # Calcul résultat financier
    resultat_financier = montant_total_adoptions - montant_total_visites
    # Moyenne du montant des visites médicales par animal et pour différents ages (age au moment de l'arrivée dans l'asso)
    chats = Animal.objects.annotate(start_year=ExtractYear('date_naissance'),
                                   start_month=ExtractMonth('date_naissance'),
                                   end_year=ExtractYear('date_arrivee'),
                                   end_month=ExtractMonth('date_arrivee'),
                ).annotate(
                    month_diff=ExpressionWrapper(
                        (F('end_year') - F('start_year')) * 12 + (F('end_month') - F('start_month')),
                        output_field=IntegerField()
                    )
                )

    chatons = chats.filter(month_diff__lt=6)
    adultes = chats.filter(month_diff__gte=6).filter(month_diff__lt=96)
    seniors = chats.filter(month_diff__gte=96)
    years = []

    if annee:
        years = [annee]
    else:
        years = [(tag.value) for tag in AnneeChoice]
        
    moyenne_par_animal = Animal.objects.annotate(
        montant_total=Sum('visites__amount_animal', filter=Q(visites__date__year__in=years))
        ).aggregate(montant_moyen=Avg('montant_total'))['montant_moyen'] or 0
    moyenne_chatons = chatons.annotate(
        montant_total=Sum('visites__amount_animal', filter=Q(visites__date__year__in=years))
        ).aggregate(montant_moyen=Avg('montant_total'))['montant_moyen'] or 0
    moyenne_adultes = adultes.annotate(
        montant_total=Sum('visites__amount_animal', filter=Q(visites__date__year__in=years))
        ).aggregate(montant_moyen=Avg('montant_total'))['montant_moyen'] or 0
    moyenne_seniors = seniors.annotate(
        montant_total=Sum('visites__amount_animal', filter=Q(visites__date__year__in=years))
        ).aggregate(montant_moyen=Avg('montant_total'))['montant_moyen'] or 0
    
    # Données pour graphique répartition par types de visites
    labels_types = ["Soins groupés", "Vaccination seule", "Stérilisation seule", "Urgence et Chirurgie", "Traitement", "Autres"]
    data_type_visites = []
    data_type_visites.append(visites.filter(visit_type__in=["PACK_TC", "PACK_TCL", "PACK_STE_TC", "PACK_STE_TCL"]).count())
    data_type_visites.append(visites.filter(visit_type__in=["TC", "TCL"]).count())
    data_type_visites.append(visites.filter(visit_type__in=["STE"]).count())
    data_type_visites.append(visites.filter(visit_type__in=["URGENCE", "CHIRURGIE"]).count())
    data_type_visites.append(visites.filter(visit_type="TRAITEMENT").count())
    data_type_visites.append(visites.filter(visit_type__in=["AUTRE",'CONSULT',"IDE","TESTS"]).count())
    



    return render(request, "gestion_association/stats.html", locals())