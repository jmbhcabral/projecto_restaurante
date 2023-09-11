# Generated by Django 4.2.5 on 2023-09-09 09:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('restau', '0022_remove_produtosfidelizacao_unidades_recompensa_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='produtosfidelizacao',
            name='ponotos_recompensa',
        ),
        migrations.AddField(
            model_name='produtosfidelizacao',
            name='pontos_recompensa',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pontos_recompensa', to='restau.products'),
        ),
    ]