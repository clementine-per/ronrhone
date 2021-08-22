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
from gestion_association.models.person import Person

class PersonResource(ModelResource):

    # Suppression des animaux pas encore adoptés
    def for_delete(self, row, instance):
        nom_prenom_key = self.fields['nom_prenom_key'].clean(row)
        print(nom_prenom_key)
        sys.stdout.flush()
        return nom_prenom_key == ""

    class Meta:
        model = Person
        import_id_fields = ('nom','nom_prenom_key')
        fields = ('nom', 'prenom','nom_prenom_key', 'code_postal', 'adresse','ville','telephone')



class AdoptionResource(ModelResource):
    adoptant = Field(column_name='nom_prenom_key', attribute='adoptant',
                         widget=ForeignKeyWidget(Person, 'nom_prenom_key'))
    animal = Field(column_name='nom_animal', attribute='animal',
                   widget=ForeignKeyWidget(Animal, 'nom'))

    # Suppression des animaux pas encore adoptés
    def for_delete(self, row, instance):
        statut = row.get('statut')
        return statut != StatutAnimal.ADOPTION.name and statut != StatutAnimal.ADOPTE.name and statut != StatutAnimal.ADOPTE_DEFINITIF.name

    def before_import_row(self, row, **kwargs):
        # Encaissement
        encaisse = row.get('encaisse')
        # Si vide, pas encaissé
        if encaisse == "":
            row['montant_restant'] = row.get('montant')
            row['acompte_verse'] =  "NON"
        # Uniquement acompte
        try:
            if "acompte" in encaisse:
                row['montant_restant'] = int(row.get('montant')) - 100
                row['acompte_verse'] = "OUI"
            else:
                row['montant_restant'] = 0
                row['acompte_verse'] = "OUI"
        except TypeError:
            row['montant_restant'] = 0
            row['acompte_verse'] = "OUI"



    class Meta:
        model = Adoption
        fields = ('id', 'adoptant', 'date', 'nom', 'montant')
        widgets = {
            'date': {'format': '%d/%m/%Y'},
        }


class AnimalResource(ModelResource):
    class Meta:
        model = Animal
        import_id_fields = ('nom',)

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