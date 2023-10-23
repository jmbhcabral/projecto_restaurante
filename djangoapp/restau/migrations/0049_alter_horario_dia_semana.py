# Generated by Django 4.2.6 on 2023-10-17 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restau', '0048_contactossite_facebook_contactossite_facebook_icon_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='horario',
            name='dia_semana',
            field=models.CharField(blank=True, choices=[('Segunda', 'Segunda-feira'), ('Terça', 'Terça-feira'), ('Quarta', 'Quarta-feira'), ('Quinta', 'Quinta-feira'), ('Sexta', 'Sexta-feira'), ('Sábado', 'Sábado'), ('Domingo', 'Domingo'), ('Feriados', 'Feriados')], default='', max_length=10, null=True, verbose_name='Dia da semana'),
        ),
    ]