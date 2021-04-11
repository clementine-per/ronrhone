# Register your models here.
from import_export.admin import ImportExportModelAdmin

from django.contrib import admin

from gestion_association.models.adoption import (
    Adoption,
    BonSterilisation,
    TarifAdoption,
    TarifBonSterilisation,
)
from gestion_association.models.animal import Animal, Preference
from gestion_association.models.famille import Accueil, Famille, Indisponibilite
from gestion_association.models.person import Person


@admin.register(Person)
class ProprietaireAdmin(ImportExportModelAdmin):
    pass


@admin.register(Animal)
class AnimalAdmin(ImportExportModelAdmin):
    pass


@admin.register(Adoption)
class AdoptionAdmin(ImportExportModelAdmin):
    pass


@admin.register(Preference)
class PreferenceAdmin(ImportExportModelAdmin):
    pass


@admin.register(Famille)
class FamilleAdmin(ImportExportModelAdmin):
    pass


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


@admin.register(Accueil)
class AccueilAdmin(ImportExportModelAdmin):
    pass
