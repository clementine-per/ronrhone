# Generated by Django 4.1.2 on 2023-03-13 10:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_association', '0017_alter_parrainage_options'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations = [
                migrations.DeleteModel(
                    name='VisiteMedicale',
                ),
            ],
            database_operations=[],
        )
    ]
