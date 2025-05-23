# Generated by Django 4.2.19 on 2025-04-02 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AppVersion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sistema_operativo', models.CharField(choices=[('android', 'Android'), ('ios', 'iOS')], max_length=10)),
                ('versao', models.CharField(max_length=20)),
                ('forcar_update', models.BooleanField(default=False)),
                ('data_lancamento', models.DateField(auto_now_add=True)),
            ],
        ),
    ]
