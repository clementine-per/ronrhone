# Register your models here.
import sys

from import_export.admin import ImportExportModelAdmin

from django.contrib import admin
from import_export.fields import Field
from import_export.resources import ModelResource
from import_export.widgets import ForeignKeyWidget

from gestion_association.models.adoption import (
    Adoption,
    BonSterilisation,
    TarifAdoption,
    TarifBonSterilisation,
)
from gestion_association.models.animal import Animal, Preference, StatutAnimal
from gestion_association.models.famille import Accueil, Famille, Indisponibilite
from gestion_association.models.person import Person, Adhesion


class PersonResource(ModelResource):

    class Meta:
        model = Person
        import_id_fields = ('nom_prenom_key',)
        fields = ('nom', 'prenom','nom_prenom_key','email',
                  'code_postal', 'adresse','ville','telephone','is_famille','is_adoptante')


class FamilleResource(ModelResource):
    personne = Field(column_name='nom_prenom_key', attribute='personne',
                         widget=ForeignKeyWidget(Person, 'nom_prenom_key'))

    class Meta:
        model = Famille
        import_id_fields = ('id',)

    def before_save_instance(self, instance, using_transactions, dry_run):
        preference = Preference.objects.create()
        instance.preference = preference
        return instance


class AccueilResource(ModelResource):
    famille = Field(column_name='famille', attribute='famille',
                         widget=ForeignKeyWidget(Famille, 'id'))
    animal = Field(column_name='nom_animal', attribute='animal',
                   widget=ForeignKeyWidget(Animal, 'nom'))

    class Meta:
        model = Accueil



class AdoptionResource(ModelResource):
    adoptant = Field(column_name='nom_prenom_key', attribute='adoptant',
                         widget=ForeignKeyWidget(Person, 'nom_prenom_key'))
    personne_visite = Field(column_name='nom_prenom_key_benevole', attribute='personne_visite',
                     widget=ForeignKeyWidget(Person, 'nom_prenom_key'))
    animal = Field(column_name='nom_animal', attribute='animal',
                   widget=ForeignKeyWidget(Animal, 'nom'))




    class Meta:
        model = Adoption
        import_id_fields = ('id',)
        widgets = {
            'date': {'format': '%d/%m/%Y'},
        }


class AnimalResource(ModelResource):
    class Meta:
        model = Animal
        import_id_fields = ('nom',)
        widgets = {
            'date_naissance' : {'format' : '%d/%m/%Y'},
            'date_arrivee': {'format': '%d/%m/%Y'},
            'date_prochain_vaccin': {'format': '%d/%m/%Y'},
            'date_vermifuge': {'format': '%d/%m/%Y'}
        }

    def before_save_instance(self, instance, using_transactions, dry_run):
        preference = Preference.objects.create()
        instance.preference = preference
        return instance


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
    pass


@admin.register(TarifBonSterilisation)
class TarifBonSterilisationAdmin(ImportExportModelAdmin):
    pass


@admin.register(BonSterilisation)
class BonSterilisationAdmin(ImportExportModelAdmin):
    pass


@admin.register(Indisponibilite)
class IndisponibiliteAdmin(ImportExportModelAdmin):
    pass

@admin.register(Adhesion)
class AdhesionAdmin(ImportExportModelAdmin):
    pass


@admin.register(Accueil)
class AccueilAdmin(ImportExportModelAdmin):
    resource_class = AccueilResource