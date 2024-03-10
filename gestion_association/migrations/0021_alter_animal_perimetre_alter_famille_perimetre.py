# Generated by Django 4.1.2 on 2024-03-10 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_association', '0020_alter_person_telephone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='animal',
            name='perimetre',
            field=models.CharField(choices=[('UN', 'Périmètre 1 (Marjo)'), ('DEUX', 'Périmètre 2 (Lucile)'), ('TROIS', 'Périmètre 3 (Mélanie)')], default='UN', max_length=30, verbose_name='Périmètre de gestion'),
        ),
        migrations.AlterField(
            model_name='famille',
            name='perimetre',
            field=models.CharField(choices=[('UN', 'Périmètre 1 (Marjo)'), ('DEUX', 'Périmètre 2 (Lucile)'), ('TROIS', 'Périmètre 3 (Mélanie)')], default='UN', max_length=30, verbose_name='Périmètre de gestion'),
        ),
    ]
