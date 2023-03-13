# Generated by Django 3.1.4 on 2022-02-06 04:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_association', '0009_famille_neko'),
    ]

    operations = [
        migrations.AlterField(
            model_name='animal',
            name='type',
            field=models.CharField(choices=[('CHAT', 'Chat'), ('CHIEN', 'Chien')], default='CHAT', max_length=30, verbose_name="Type d'animal"),
        ),
        migrations.CreateModel(
            name='VisiteMedicale',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_mise_a_jour', models.DateField(auto_now=True, verbose_name='Date de mise à jour')),
                ('date', models.DateField(verbose_name='Date de la visite')),
                ('type_visite', models.CharField(choices=[('VAC_PRIMO_TC', 'Primo vaccination TC'), ('VAC_PRIMO_TCL', 'Primo vaccination TCL'), ('VAC_RAPPEL_TC', 'Rappel vaccination TC'), ('VAC_RAPPEL_TCL', 'Rappel vaccination TCL'), ('STE', 'Stérilisation'), ('TESTS', 'Tests FIV/FELV'), ('IDE', 'Identification'), ('CONSULT', 'Consultation'), ('PACK_TC', 'Identification, primo vaccination TC, Tests FIV/FELV'), ('PACK_TCL', 'Identification, primo vaccination TCL, Tests FIV/FELV'), ('AUTRE', 'Autre')], max_length=30, verbose_name='Objet de la visite')),
                ('veterinaire', models.CharField(blank=True, max_length=150)),
                ('commentaire', models.CharField(blank=True, max_length=2000)),
                ('montant', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True, verbose_name='Montant')),
                ('animaux', models.ManyToManyField(related_name='visites', to='gestion_association.Animal')),
            ],
        ),
    ]
