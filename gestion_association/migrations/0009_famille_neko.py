# Generated by Django 3.1.4 on 2022-01-22 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_association', '0008_animal_inactif'),
    ]

    operations = [
        migrations.AddField(
            model_name='famille',
            name='neko',
            field=models.BooleanField(default=False, verbose_name="Il s'agit du café des chats (Neko)"),
        ),
    ]