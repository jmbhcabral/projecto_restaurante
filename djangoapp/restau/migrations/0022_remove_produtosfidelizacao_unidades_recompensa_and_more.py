# Generated by Django 4.2.5 on 2023-09-09 09:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('restau', '0021_produtosfidelizacao_fidelizacao_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='produtosfidelizacao',
            name='unidades_recompensa',
        ),
        migrations.AddField(
            model_name='produtosfidelizacao',
            name='ponotos_recompensa',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pontos_recompensa', to='restau.products'),
        ),
    ]