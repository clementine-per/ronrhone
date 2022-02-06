from django.db.models import BLANK_CHOICE_DASH
from django.forms import Form, CharField, ChoiceField, Select, ModelForm, DateField, DateInput

from gestion_association.models.animal import Animal, statuts_association
from gestion_association.models.visite_medicale import TypeVisiteVetoChoice, VisiteMedicale


class DateInput(DateInput):
    input_type = "date"


class VisiteMedicaleSearchForm(Form):
    veterinaire = CharField(max_length=150, required=False)
    type_visite = ChoiceField(
        choices=BLANK_CHOICE_DASH + [(tag.name, tag.value) for tag in TypeVisiteVetoChoice],
        widget=Select(),
        required=False,
        label="Type de visite",
    )
    date_min = DateField(
        label="Date de la visite médicale entre le", required=False, widget=DateInput()
    )
    date_max = DateField(label=" et le ", required=False, widget=DateInput())


class VisiteMedicaleForm(ModelForm):
    # Pour mettre les champs obligatoires en gras
    required_css_class = 'required'
    class Meta:
        model = VisiteMedicale
        fields = (
            "date",
            "type_visite",
            "veterinaire",
            "commentaire",
            "montant",
            "animaux",
        )

    def __init__(self, *args, **kwargs):
        super(VisiteMedicaleForm, self).__init__(*args, **kwargs)
        self.fields['date'].widget.attrs['class'] = 'datePicker'
        self.fields['animaux'].queryset = Animal.objects.filter(inactif=False).filter(statut__in=statuts_association).order_by('nom')