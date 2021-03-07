from django.contrib import admin

# Register your models here.
from import_export.admin import ImportExportModelAdmin

from gestion_association.models.adoption import TarifAdoption, Adoption, TarifBonSterilisation
from gestion_association.models.animal import Animal, Preference
from gestion_association.models.famille import Famille
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