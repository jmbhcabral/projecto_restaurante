# Generated by Django 4.2.3 on 2024-02-25 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('perfil', '0015_passwordresettoken'),
    ]

    operations = [
        migrations.AlterField(
            model_name='perfil',
            name='estudante',
            field=models.CharField(blank=True, help_text='Se estudante, indique a escola onde estuda.', max_length=255, null=True, verbose_name='Estudante'),
        ),
    ]
