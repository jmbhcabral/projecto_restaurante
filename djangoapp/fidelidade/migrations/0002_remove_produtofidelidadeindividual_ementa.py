# Generated by Django 4.2.5 on 2023-09-18 16:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fidelidade', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='produtofidelidadeindividual',
            name='ementa',
        ),
    ]
