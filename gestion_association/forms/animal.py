from dal import autocomplete

from django.db.models import BLANK_CHOICE_DASH
from django.forms import (
    CharField,
    ChoiceField,
    DateField,
    DateInput,
    Form,
    ModelForm,
    ModelMultipleChoiceField,
    MultipleChoiceField,
    Select,
    SelectMultiple)

from gestion_association.models import OuiNonChoice, PerimetreChoice
from gestion_association.models.animal import Animal, StatutAnimal, statuts_association, Parrainage
from gestion_association.models.person import Person
from gestion_association.widgets import TableSelectMultiple


class DateInput(DateInput):
    input_type = "date"

class AnimalSearchForm(Form):
    nom = CharField(max_length=100, required=False)
    identification = CharField(max_length=100, required=False, label="Numéro d'identification")
    perimetre = ChoiceField(
        choices=BLANK_CHOICE_DASH + [(tag.name, tag.value) for tag in PerimetreChoice],
        widget=Select(),
        required=False,
        label="Périmètre de gestion"
    )
    sterilise = ChoiceField(
        choices=BLANK_CHOICE_DASH + [(tag.name, tag.value) for tag in OuiNonChoice],
        widget=Select(),
        required=False,
    )
    fiv_felv = ChoiceField(
        choices=BLANK_CHOICE_DASH + [(tag.name, tag.value) for tag in OuiNonChoice],
        widget=Select(),
        required=False,
        label= "Testé FIV et FELV"
    )
    date_naissance_min = DateField(
        label="Date de naissance entre le", required=False, widget=DateInput()
    )
    date_naissance_max = DateField(label=" et le ", required=False, widget=DateInput())
    date_arrivee_min = DateField(
        label="Date de prise en charge entre le", required=False, widget=DateInput()
    )
    date_arrivee_max = DateField(label=" et le ", required=False, widget=DateInput())
    date_prochain_vaccin_min = DateField(
        label="Date du prochain vaccin entre le",
        required=False,
        widget=DateInput(),
    )
    date_prochain_vaccin_max = DateField(label=" et le ", required=False, widget=DateInput())
    sans_fa = ChoiceField(
        choices=BLANK_CHOICE_DASH + [(tag.name, tag.value) for tag in OuiNonChoice],
        widget=Select(),
        required=False,
    )
    statuts = MultipleChoiceField(
        choices=[(tag.name, tag.value) for tag in StatutAnimal],
        required=False,
        widget=SelectMultiple(attrs={'class':"selectpicker"})
    )
    nekosable = ChoiceField(
        choices=BLANK_CHOICE_DASH + [(tag.name, tag.value) for tag in OuiNonChoice],
        widget=Select(),
        required=False,
    )

class AnimalCreateForm(ModelForm):
    # Pour mettre les champs obligatoires en gras
    required_css_class = 'required'
    class Meta:
        model = Animal
        fields = (
            "nom",
            "sexe",
            "date_naissance",
            "identification",
            "perimetre",
            "circonstances",
            "date_arrivee",
            "commentaire",
            "statut",
            "sterilise",
            "date_sterilisation",
            "type_vaccin",
            "primo_vaccine",
            "vaccin_ok",
            "date_prochain_vaccin",
            "fiv",
            "felv",
            "date_parasite",
            "date_vermifuge",
            "commentaire_sante",
            "lien_icad",
            "nekosable",
            "ancien_proprio",
        )
        widgets = {
            'ancien_proprio': autocomplete.ModelSelect2(url='person_autocomplete')
        }


    def __init__(self, *args, **kwargs):
        super(AnimalCreateForm, self).__init__(*args, **kwargs)
        self.fields['date_naissance'].widget.attrs['class'] = 'datePicker'
        self.fields['date_arrivee'].widget.attrs['class'] = 'datePicker'
        self.fields['date_sterilisation'].widget.attrs['class'] = 'datePicker'
        self.fields['date_prochain_vaccin'].widget.attrs['class'] = 'datePicker'
        self.fields['date_parasite'].widget.attrs['class'] = 'datePicker'
        self.fields['date_vermifuge'].widget.attrs['class'] = 'datePicker'
        self.fields['ancien_proprio'].queryset = Person.objects.filter(inactif=False).order_by('nom')


class AnimalOtherInfosForm(ModelForm):
    # Pour mettre les champs obligatoires en gras
    required_css_class = 'required'
    class Meta:
        model = Animal
        fields = ("tranche_age","commentaire_animaux_lies")


class AnimalSelectForm(Form):
    animaux = ModelMultipleChoiceField(
        required=False,
        widget=SelectMultiple(attrs={'class': "selectpicker"}),
        queryset=Animal.objects.filter(inactif=False).order_by('nom'),
    )


class AnimalInfoUpdateForm(ModelForm):
    # Pour mettre les champs obligatoires en gras
    required_css_class = 'required'
    class Meta:
        model = Animal
        fields = (
            "nom",
            "sexe",
            "date_naissance",
            "identification",
            "perimetre",
            "circonstances",
            "date_arrivee",
            "commentaire",
            "statut",
            "lien_icad",
            "nekosable",
            "ancien_proprio",
            "inactif",
        )
        widgets = {
            'ancien_proprio': autocomplete.ModelSelect2(url='person_autocomplete')
        }

    def __init__(self, *args, **kwargs):
        super(AnimalInfoUpdateForm, self).__init__(*args, **kwargs)
        self.fields['date_naissance'].widget.attrs['class'] = 'datePicker'
        self.fields['date_arrivee'].widget.attrs['class'] = 'datePicker'
        self.fields['ancien_proprio'].queryset = Person.objects.filter(inactif=False).order_by('nom')


class AnimalSanteUpdateForm(ModelForm):
    # Pour mettre les champs obligatoires en gras
    required_css_class = 'required'
    class Meta:
        model = Animal
        fields = (
            "sterilise",
            "date_sterilisation",
            "type_vaccin",
            "primo_vaccine",
            "vaccin_ok",
            "date_prochain_vaccin",
            "fiv",
            "felv",
            "date_parasite",
            "date_vermifuge",
            "commentaire_sante"
        )

    def __init__(self, *args, **kwargs):
        super(AnimalSanteUpdateForm, self).__init__(*args, **kwargs)
        self.fields['date_sterilisation'].widget.attrs['class'] = 'datePicker'
        self.fields['date_prochain_vaccin'].widget.attrs['class'] = 'datePicker'
        self.fields['date_parasite'].widget.attrs['class'] = 'datePicker'
        self.fields['date_vermifuge'].widget.attrs['class'] = 'datePicker'

class AnimalSelectForFaForm(Form):
    animaux = ModelMultipleChoiceField(
        queryset=Animal.objects.filter(statut__in=statuts_association).filter(inactif=False).filter(famille__isnull=True),
        widget=TableSelectMultiple(
            item_attrs=[
                'nom',
                ('get_statut_display', "Statut"),
                'preference',
                ('get_animaux_lies_str', "Animaux liés"),

            ],
            enable_shift_select=True,
            enable_datatables=True,
            bootstrap_style=True,
        ), required=False
    )


class ParrainageForm(ModelForm):
    required_css_class = 'required'

    class Meta:
        model = Parrainage
        fields = (
            "date_debut",
            "date_fin",
            "animal",
            "date_nouvelles",
            "type_paiement",
            "montant"
        )

    def __init__(self, *args, **kwargs):
        super(ParrainageForm, self).__init__(*args, **kwargs)
        queryset = Animal.objects.filter(inactif=False).filter(statut__in=statuts_association)
        try:
            animal = self.instance.animal
        except Parrainage._meta.model.animal.RelatedObjectDoesNotExist:
            animal = None
        if animal:
            queryset = queryset | Animal.objects.filter(id=animal.pk)
        self.fields['animal'].queryset = queryset
        self.fields['date_debut'].widget.attrs['class'] = 'datePicker'
        self.fields['date_fin'].widget.attrs['class'] = 'datePicker'
        self.fields['date_nouvelles'].widget.attrs['class'] = 'datePicker'


