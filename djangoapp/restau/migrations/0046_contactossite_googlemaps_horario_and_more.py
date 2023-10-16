# Generated by Django 4.2.6 on 2023-10-16 09:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('restau', '0045_alter_frasebaixo_texto_alter_frasecima_texto_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactosSite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('morada', models.TextField(blank=True, default='', max_length=250, null=True, verbose_name='Morada')),
                ('telefone', models.CharField(blank=True, default='', max_length=15, null=True, verbose_name='Telefone')),
                ('email', models.CharField(blank=True, default='', max_length=50, null=True, verbose_name='Email')),
            ],
            options={
                'verbose_name': 'Contacto Site',
                'verbose_name_plural': 'Contactos Site',
            },
        ),
        migrations.CreateModel(
            name='GoogleMaps',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('iframe', models.TextField(blank=True, default='', max_length=250, null=True, verbose_name='Iframe')),
            ],
            options={
                'verbose_name': 'Google Maps',
                'verbose_name_plural': 'Google Maps',
            },
        ),
        migrations.CreateModel(
            name='Horario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dia_semana', models.CharField(blank=True, choices=[('Segunda', 'Segunda-feira'), ('Terça', 'Terça-feira'), ('Quarta', 'Quarta-feira'), ('Quinta', 'Quinta-feira'), ('Sexta', 'Sexta-feira'), ('Sábado', 'Sábado'), ('Domingo', 'Domingo')], default='', max_length=10, null=True, verbose_name='Dia da semana')),
                ('hora_abertura_almoco', models.TimeField(blank=True, null=True, verbose_name='Hora de abertura do almoço')),
                ('hora_fecho_almoco', models.TimeField(blank=True, null=True, verbose_name='Hora de fecho do almoço')),
                ('hora_abertura_jantar', models.TimeField(blank=True, null=True, verbose_name='Hora de abertura do jantar')),
                ('hora_fecho_jantar', models.TimeField(blank=True, null=True, verbose_name='Hora de fecho do jantar')),
                ('status', models.CharField(blank=True, choices=[('Aberto', 'Aberto'), ('Encerrado', 'Encerrado')], default='Aberto', max_length=10, null=True, verbose_name='Folga')),
                ('dia_encerramento', models.CharField(blank=True, choices=[('Segunda', 'Segunda-feira'), ('Terça', 'Terça-feira'), ('Quarta', 'Quarta-feira'), ('Quinta', 'Quinta-feira'), ('Sexta', 'Sexta-feira'), ('Sábado', 'Sábado'), ('Domingo', 'Domingo')], default='Domingo', max_length=10, null=True, verbose_name='Dia de encerramento')),
            ],
            options={
                'verbose_name': 'Horário',
                'verbose_name_plural': 'Horários',
            },
        ),
        migrations.AddField(
            model_name='activesetup',
            name='active_contactos_site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='active_contactos_site_set', to='restau.contactossite'),
        ),
        migrations.AddField(
            model_name='activesetup',
            name='active_google_maps',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='active_google_maps_set', to='restau.googlemaps'),
        ),
    ]
