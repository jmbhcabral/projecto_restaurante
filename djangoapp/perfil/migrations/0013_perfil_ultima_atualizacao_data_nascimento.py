# Generated by Django 4.2.6 on 2023-10-06 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('perfil', '0012_perfil_estudante'),
    ]

    operations = [
        migrations.AddField(
            model_name='perfil',
            name='ultima_atualizacao_data_nascimento',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]