from django.contrib import admin

# Register your models here.
from import_export.admin import ImportExportModelAdmin

from gestion_association.models.animal import Animal, Adoption
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
