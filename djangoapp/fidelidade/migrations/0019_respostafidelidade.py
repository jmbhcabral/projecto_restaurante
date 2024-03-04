# Generated by Django 4.2.3 on 2024-02-25 13:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fidelidade', '0018_perguntas_respostas'),
    ]

    operations = [
        migrations.CreateModel(
            name='RespostaFidelidade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resposta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fidelidade.respostas', verbose_name='Resposta')),
                ('tipo_fidelidade', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fidelidade.fidelidade', verbose_name='Tipo Fidelidade')),
                ('utilizador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Utilizador')),
            ],
            options={
                'verbose_name': 'Resposta Fidelidade',
                'verbose_name_plural': 'Respostas Fidelidade',
            },
        ),
    ]
