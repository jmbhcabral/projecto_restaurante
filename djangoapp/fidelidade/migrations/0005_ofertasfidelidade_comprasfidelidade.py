# Generated by Django 4.2.5 on 2023-09-22 08:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fidelidade', '0004_alter_produtofidelidadeindividual_produto'),
    ]

    operations = [
        migrations.CreateModel(
            name='OfertasFidelidade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pontos_gastos', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Pontos Adicionados')),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('fidelidade', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fidelidade.fidelidade')),
                ('utilizador', models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Compra Fidelidade',
                'verbose_name_plural': 'Compras Fidelidade',
            },
        ),
        migrations.CreateModel(
            name='ComprasFidelidade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pontos_adicionados', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Pontos Adicionados')),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('fidelidade', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fidelidade.fidelidade')),
                ('utilizador', models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Compra Fidelidade',
                'verbose_name_plural': 'Compras Fidelidade',
            },
        ),
    ]