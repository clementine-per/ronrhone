# Register your models here.
from import_export.admin import ImportExportModelAdmin

from django.contrib import admin
from import_export.fields import Field
from import_export.resources import ModelResource
from import_export.widgets import ForeignKeyWidget, DateWidget

from gestion_association.models.adoption import (
    Adoption,
    BonSterilisation,
    TarifAdoption,
    TarifBonSterilisation,
)
from gestion_association.models.animal import Animal, Preference
from gestion_association.models.famille import Accueil, Famille, Indisponibilite
from gestion_association.models.person import Person, Adhesion
from medical_visit.models import VisiteMedicale


class PersonResource(ModelResource):
    is_famille = Field(column_name="Famille d'accueil", attribute='is_famille')
    is_adoptante = Field(column_name="Adoptant", attribute='is_adoptante')

    class Meta:
        model = Person
        import_id_fields = ('nom_prenom_key',)
        fields = ('nom', 'prenom','email',
                  'code_postal', 'adresse','ville','telephone','is_famille','is_adoptante')
        export_order = ('nom', 'prenom','email',
                  'adresse','code_postal','ville','telephone','is_famille','is_adoptante')


class FamilleResource(ModelResource):
    personne = Field(column_name='Nom/Prénom', attribute='personne',
                         widget=ForeignKeyWidget(Person, 'nom_prenom_key'))
    nb_animaux_historique = Field(column_name="Nombre d'animaux accueillis", attribute='nb_animaux_historique')
    taille_logement = Field(column_name="Espace du logement", attribute='taille_logement')
    longue_duree = Field(column_name="Longue durée", attribute='longue_duree')
    nb_places = Field(column_name="Nombre de places", attribute='nb_places')
    detail_places = Field(column_name="Détails sur les places", attribute='detail_places')
    type_animal = Field(column_name="Type", attribute='type_animal')
    autres_animaux = Field(column_name="Autres animaux", attribute='autres_animaux')
    nb_heures_absence = Field(column_name="Heures d'absence consécutives maximum", attribute='nb_heures_absence')
    neko = Field(column_name="Café des chats (Neko)", attribute='neko')

    class Meta:
        model = Famille
        import_id_fields = ('id',)
        # Revoir préférence
        exclude = ('id', 'date_mise_a_jour', 'preference',)

    def before_save_instance(self, instance, using_transactions, dry_run):
        preference = Preference.objects.create()
        instance.preference = preference
        return instance


class AccueilResource(ModelResource):
    famille = Field(column_name='Famille', attribute='famille',
                         widget=ForeignKeyWidget(Famille, 'personne'))
    animal = Field(column_name='Animaux', attribute='animal',
                   widget=ForeignKeyWidget(Animal, 'nom'))
    date_debut = Field(column_name='Date de début', attribute='date_debut', widget=DateWidget('%d/%m/%Y'))
    date_fin = Field(column_name='Date de fin', attribute='date_fin', widget=DateWidget('%d/%m/%Y'))
    statut = Field(column_name="Statut de l'accueil", attribute='statut')

    class Meta:
        model = Accueil
        exclude = ('id',)



class AdoptionResource(ModelResource):
    adoptant = Field(column_name="Nom de l'Adoptant", attribute='adoptant',
                         widget=ForeignKeyWidget(Person, 'nom_prenom_key'))
    personne_visite = Field(column_name='Nom du Bénévole', attribute='personne_visite',
                     widget=ForeignKeyWidget(Person, 'nom_prenom_key'))
    animal = Field(column_name='Animaux', attribute='animal',
                   widget=ForeignKeyWidget(Animal, 'nom'))
    date = Field(column_name="Date d'adoption", attribute='date', widget=DateWidget('%d/%m/%Y'))
    # TODO : Trouver comment faire pour afficher MontantRestant/Montant, et ajouter '€'
    montant_restant = Field(column_name='Montant Restant à payer', attribute='montant_restant')
    montant = Field(column_name='Montant Total', attribute='montant')
    nb_jours = Field(column_name='Nombre de jours avant Adoption', attribute='nb_jours')
    pre_visite = Field(column_name='Visite pré-adoption', attribute='pre_visite')
    # TODO : Mettre une condition pour que si la visite de contrôle est NON, date_visite affiche NON
    date_visite = Field(column_name='Date de la visite de contrôle', attribute='date_visite', widget=DateWidget('%d/%m/%Y'))
    acompte_verse = Field(column_name='Acompte versé', attribute='acompte_verse')

    class Meta:
        model = Adoption
        import_id_fields = ('id',)
        exclude = ('id', 'visite_controle', 'annule',)

    # Supprime tout ce qui est annulé, TODO : Juste les barrer
    def export(self, queryset=None, *args, **kwargs):
        queryset = queryset and queryset.filter(annule__in=[0])
        return super(AdoptionResource, self).export(queryset, *args, **kwargs)

class AnimalResource(ModelResource):
    # circonstances de récupération

    class Meta:
        model = Animal
        import_id_fields = ('nom',)
        widgets = {
            'date_naissance' : {'format' : '%d/%m/%Y'},
            'date_arrivee': {'format': '%d/%m/%Y'},
            'date_prochain_vaccin': {'format': '%d/%m/%Y'},
            'date_vermifuge': {'format': '%d/%m/%Y'}
        }
        exclude = ('id', 'date_mise_a_jour',)

    def before_save_instance(self, instance, using_transactions, dry_run):
        preference = Preference.objects.create()
        instance.preference = preference
        return instance

class AdhesionResource(ModelResource):
    personne = Field(column_name='Nom/Prenom', attribute='personne',
                     widget=ForeignKeyWidget(Person, 'nom_prenom_key'))
    date = Field(attribute='date', column_name="Date d'adhésion", widget=DateWidget('%d/%m/%Y'))
    montant = Field(attribute='montant', column_name='Montant Cotisation')

    class Meta:
        model = Adhesion
        import_id_fields = ('nom_prenom_key',)
        exclude = ('id',)

class BonSterilisationResource(ModelResource):
    # TODO : Mettre le nom de l'adoptant et celui de l'animal
    '''adoption = Field(column_name='Adoptant', attribute='adoption',
                     widget=ForeignKeyWidget(Adoption, ''))'''
    envoye = Field(attribute='envoye', column_name="A été envoyé")
    date_max = Field(attribute='date_max', column_name="Date limite", widget=DateWidget('%d/%m/%Y'))
    date_utilisation = Field(attribute='date_utilisation', column_name="Date d'utilisation", widget=DateWidget('%d/%m/%Y'))

    class Meta:
        model = BonSterilisation
        exclude = ('id', 'utilise',)

class TarifBonSterilisationResource(ModelResource):
    type_animal = Field(attribute='type_animal', column_name="Type")

    class Meta:
        model = TarifBonSterilisation
        exclude = ('id',)

class TarifAdoptionResource(ModelResource):
    type_animal = Field(attribute='type_animal', column_name="Type")

    class Meta:
        model = TarifBonSterilisation
        exclude = ('id',)

@admin.register(Person)
class PersonAdmin(ImportExportModelAdmin):
    resource_class = PersonResource


@admin.register(Animal)
class AnimalAdmin(ImportExportModelAdmin):
    resource_class = AnimalResource


@admin.register(Adoption)
class AdoptionAdmin(ImportExportModelAdmin):
    resource_class = AdoptionResource


@admin.register(Preference)
class PreferenceAdmin(ImportExportModelAdmin):
    pass


@admin.register(Famille)
class FamilleAdmin(ImportExportModelAdmin):
    resource_class = FamilleResource


@admin.register(TarifAdoption)
class TarifAdoptionAdmin(ImportExportModelAdmin):
    resource_class = TarifAdoptionResource


@admin.register(TarifBonSterilisation)
class TarifBonSterilisationAdmin(ImportExportModelAdmin):
    resource_class = TarifBonSterilisationResource


@admin.register(BonSterilisation)
class BonSterilisationAdmin(ImportExportModelAdmin):
    resource_class = BonSterilisationResource


@admin.register(Indisponibilite)
class IndisponibiliteAdmin(ImportExportModelAdmin):
    pass

@admin.register(VisiteMedicale)
class VisiteMedicaleAdmin(ImportExportModelAdmin):
    pass

@admin.register(Adhesion)
class AdhesionAdmin(ImportExportModelAdmin):
    resource_class = AdhesionResource


@admin.register(Accueil)
class AccueilAdmin(ImportExportModelAdmin):
    resource_class = AccueilResource