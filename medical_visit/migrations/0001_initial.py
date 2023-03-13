# Generated by Django 4.1.2 on 2023-03-13 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('gestion_association', '__first__'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='VisiteMedicale',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('date_mise_a_jour', models.DateField(auto_now=True, verbose_name='Date de mise à jour')),
                        ('date', models.DateField(verbose_name='Date de la visite')),
                        ('type_visite', models.CharField(choices=[('VAC_PRIMO_TC', 'Primo vaccination TC'), ('VAC_PRIMO_TCL', 'Primo vaccination TCL'), ('VAC_RAPPEL_TC', 'Rappel vaccination TC'), ('VAC_RAPPEL_TCL', 'Rappel vaccination TCL'), ('STE', 'Stérilisation'), ('TESTS', 'Tests FIV/FELV'), ('IDE', 'Identification'), ('CONSULT', 'Consultation'), ('PACK_TC', 'Identification, primo vaccination TC, Tests FIV/FELV'), ('PACK_TCL', 'Identification, primo vaccination TCL, Tests FIV/FELV'), ('PACK_STE_TC', 'Stérilisation, Identification, primo vaccination TC, Tests FIV/FELV'), ('PACK_STE_TCL', 'Stérilisation, Identification, primo vaccination TCL, Tests FIV/FELV'), ('AUTRE', 'Autre'), ('CHIRURGIE', 'Chirurgie'), ('URGENCE', 'Urgence')], max_length=30, verbose_name='Objet de la visite')),
                        ('veterinaire', models.CharField(blank=True, max_length=150)),
                        ('commentaire', models.CharField(blank=True, max_length=2000)),
                        ('montant', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True, verbose_name='Montant')),
                        ('animaux', models.ManyToManyField(db_table='gestion_association_visitemedicale_animaux', related_name='visites', to='gestion_association.animal')),
                    ],
                    options={
                        'db_table': 'gestion_association_visitemedicale',
                        'ordering': ['-date'],
                    },
                ),
            ],
            database_operations=[],
        )
    ]
