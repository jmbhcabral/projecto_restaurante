# Generated by Django 4.2.9 on 2024-01-22 19:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fidelidade', '0014_alter_produtofidelidadeindividual_pontos_para_oferta_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comprasfidelidade',
            name='pontos_adicionados',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True, verbose_name='Pontos Adicionados'),
        ),
    ]
