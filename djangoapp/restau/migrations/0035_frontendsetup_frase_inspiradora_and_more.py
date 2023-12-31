# Generated by Django 4.2.6 on 2023-10-10 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restau', '0034_frontendsetup_intro_frontendsetup_intro_imagem'),
    ]

    operations = [
        migrations.AddField(
            model_name='frontendsetup',
            name='frase_inspiradora',
            field=models.TextField(blank=True, default=None, max_length=250, null=True, verbose_name='Frase inspiradora'),
        ),
        migrations.AddField(
            model_name='frontendsetup',
            name='imagem_frase_baixo',
            field=models.ImageField(blank=True, default='', null=True, upload_to='assets/frontend/forntendsetup/', verbose_name='Imagem frase baixo'),
        ),
        migrations.AddField(
            model_name='frontendsetup',
            name='imagem_frase_cima',
            field=models.ImageField(blank=True, default='', null=True, upload_to='assets/frontend/forntendsetup/', verbose_name='Imagem frase cima'),
        ),
    ]
