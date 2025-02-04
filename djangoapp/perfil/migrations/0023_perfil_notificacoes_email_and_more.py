# Generated by Django 4.2.17 on 2025-02-04 01:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('perfil', '0022_perfil_data_cancelamento'),
    ]

    operations = [
        migrations.AddField(
            model_name='perfil',
            name='notificacoes_email',
            field=models.BooleanField(default=True, verbose_name='Notificações por Email'),
        ),
        migrations.AddField(
            model_name='perfil',
            name='notificacoes_telemovel',
            field=models.BooleanField(default=True, verbose_name='Notificações por Telemóvel'),
        ),
    ]
