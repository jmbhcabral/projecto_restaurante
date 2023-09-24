# Generated by Django 4.2.5 on 2023-09-14 07:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('restau', '0028_alter_produtosementa_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='produtosementa',
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name='produtosementa',
            name='ementa',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ementas', to='restau.ementa', verbose_name='Ementa'),
        ),
        migrations.RemoveField(
            model_name='produtosementa',
            name='produto',
        ),
        migrations.AddField(
            model_name='produtosementa',
            name='produto',
            field=models.ManyToManyField(related_name='produtos', to='restau.products', verbose_name='Produto'),
        ),
    ]