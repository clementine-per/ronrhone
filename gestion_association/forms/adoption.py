from django.forms import ModelForm

from gestion_association.models.animal import Adoption, Animal, StatutAnimal


class AdoptionCreateFormNoAdoptant(ModelForm):
    class Meta:
        model = Adoption
        fields = ("date","montant","montant_restant","pre_visite","visite_controle","personne_visite","date_visite")


class AdoptionCreateForm(ModelForm):
    class Meta:
        model = Adoption
        fields = ("date","adoptant","montant","montant_restant",
                  "pre_visite","visite_controle","personne_visite","date_visite")


class AdoptionFromUserForm(ModelForm):
    class Meta:
        model = Adoption
        fields = ("date", "animal", "montant", "montant_restant",
                  "pre_visite", "visite_controle", "personne_visite", "date_visite")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["animal"].queryset = Animal.objects.filter(statut=StatutAnimal.A_ADOPTER.name)


class AdoptionUpdateForm(ModelForm):
    class Meta:
        model = Adoption
        fields = ("date","montant","montant_restant",
                  "pre_visite","visite_controle","personne_visite","date_visite")