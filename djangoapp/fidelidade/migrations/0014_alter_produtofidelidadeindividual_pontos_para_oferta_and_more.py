# Generated by Django 4.2.5 on 2023-09-29 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fidelidade', '0013_alter_produtofidelidadeindividual_pontos_para_oferta_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='produtofidelidadeindividual',
            name='pontos_para_oferta',
            field=models.IntegerField(verbose_name='Pontos para Oferta'),
        ),
        migrations.AlterField(
            model_name='produtofidelidadeindividual',
            name='pontos_recompensa',
            field=models.IntegerField(verbose_name='Pontos Recompensa'),
        ),
    ]