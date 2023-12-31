# Generated by Django 4.2.6 on 2023-10-20 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restau', '0051_remove_imagemlogo_checkbox'),
    ]

    operations = [
        migrations.AlterField(
            model_name='frasebaixo',
            name='is_visible',
            field=models.BooleanField(default=False, help_text='Visibilidade da frase baixo.', verbose_name='Visibilidade'),
        ),
        migrations.AlterField(
            model_name='frasecima',
            name='is_visible',
            field=models.BooleanField(default=False, help_text='Visibilidade da frase cima.', verbose_name='Visibilidade'),
        ),
        migrations.AlterField(
            model_name='fraseinspiradora',
            name='is_visible',
            field=models.BooleanField(default=False, help_text='Visibilidade da frase inspiradora.', verbose_name='Visibilidade'),
        ),
        migrations.AlterField(
            model_name='imagemfrasebaixo',
            name='is_visible',
            field=models.BooleanField(default=False, help_text='Visibilidade da imagem.', verbose_name='Visibilidade'),
        ),
        migrations.AlterField(
            model_name='imagemfrasecima',
            name='is_visible',
            field=models.BooleanField(default=False, help_text='Visibilidade da imagem.', verbose_name='Visibilidade'),
        ),
        migrations.AlterField(
            model_name='imagempadrao',
            name='is_visible',
            field=models.BooleanField(default=False, help_text='Visibilidade da imagem.', verbose_name='Visibilidade'),
        ),
        migrations.AlterField(
            model_name='intro',
            name='is_visible',
            field=models.BooleanField(default=False, help_text='Visibilidade da intro.', verbose_name='Visibilidade'),
        ),
        migrations.AlterField(
            model_name='introimagem',
            name='is_visible',
            field=models.BooleanField(default=False, help_text='Visibilidade da imagem.', verbose_name='Visibilidade'),
        ),
    ]
