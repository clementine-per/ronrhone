# Generated by Django 4.1.2 on 2023-06-16 11:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_association', '0019_alter_animal_statut'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='telephone',
            field=models.CharField(max_length=14),
        ),
    ]
