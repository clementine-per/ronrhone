from django.forms import ModelForm

from gestion_association.models.animal import Adoption


class AdoptionCreateFormNoAdoptant(ModelForm):
    class Meta:
        model = Adoption
        fields = ("date","montant","montant_restant","pre_visite","visite_controle","personne_visite","date_visite")


class AdoptionCreateForm(ModelForm):
    class Meta:
        model = Adoption
        fields = ("date","adoptant","montant","montant_restant",
                  "pre_visite","visite_controle","personne_visite","date_visite")