# Generated by Django 4.2.5 on 2023-09-19 07:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('restau', '0031_remove_produtosfidelizacao_fidelizacao_and_more'),
        ('fidelidade', '0002_remove_produtofidelidadeindividual_ementa'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='produtofidelidadeindividual',
            options={'verbose_name': 'Produto Fidelidade Individual', 'verbose_name_plural': 'Produtos Fidelidade Individual'},
        ),
        migrations.AlterField(
            model_name='produtofidelidadeindividual',
            name='produto',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='restau.products'),
        ),
    ]
