# Generated by Django 4.2.15 on 2024-08-17 16:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fidelidade', '0023_ofertasfidelidade_processado_and_more'),
        ('perfil', '0017_perfil_ultima_actividade'),
    ]

    operations = [
        migrations.AlterField(
            model_name='perfil',
            name='estudante',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='fidelidade.respostafidelidade', verbose_name='Estudante'),
        ),
    ]
