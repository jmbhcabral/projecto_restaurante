# Generated by Django 4.2.5 on 2023-09-23 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('perfil', '0007_alter_perfil_qr_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='perfil',
            name='numero_cliente',
            field=models.CharField(blank=True, max_length=10, verbose_name='Número Cliente'),
        ),
    ]
