# Generated by Django 4.2.6 on 2023-10-10 16:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('restau', '0037_remove_activesetup_ementa_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='activesetup',
            name='active_frase_baixo',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='active_frase_baixo_set', to='restau.frontendsetup'),
        ),
        migrations.AddField(
            model_name='activesetup',
            name='active_frase_cima',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='active_frase_cima_set', to='restau.frontendsetup'),
        ),
        migrations.AddField(
            model_name='frontendsetup',
            name='frase_baixo',
            field=models.TextField(blank=True, default=None, max_length=250, null=True, verbose_name='Frase baixo'),
        ),
        migrations.AddField(
            model_name='frontendsetup',
            name='frase_cima',
            field=models.TextField(blank=True, default=None, max_length=250, null=True, verbose_name='Frase cima'),
        ),
    ]