# Generated by Django 4.2.14 on 2024-08-12 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Senhas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.IntegerField(help_text='Número da senha', verbose_name='Número')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
