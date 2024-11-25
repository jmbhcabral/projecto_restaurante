# Generated by Django 4.2.16 on 2024-11-21 18:40

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('perfil', '0018_alter_perfil_estudante'),
    ]

    operations = [
        migrations.AddField(
            model_name='perfil',
            name='reset_password_code',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='Código de Reset de Password'),
        ),
        migrations.AddField(
            model_name='perfil',
            name='reset_password_code_expires',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True, verbose_name='Expiração do Código de Reset de Password'),
        ),
    ]