from django.contrib import admin

# Register your models here.
from import_export.admin import ImportExportModelAdmin

from gestion_association.models.animal import Animal, Adoption, Preference
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