# Generated by Django 4.2.4 on 2023-08-16 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restau', '0014_remove_products_imagem_padrao_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='products',
            name='imagem',
            field=models.ImageField(blank=True, default='', null=True, upload_to='assets/Products/', verbose_name='Imagem'),
        ),
    ]
