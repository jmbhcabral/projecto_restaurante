# Generated by Django 4.2.15 on 2024-08-19 18:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('senhas', '0003_frasepub_remove_senhas_frase_pub'),
    ]

    operations = [
        migrations.AddField(
            model_name='frasepub',
            name='escolhida',
            field=models.BooleanField(default=False, help_text='Frase escolhida', verbose_name='Escolhida'),
        ),
    ]
