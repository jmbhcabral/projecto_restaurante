# Generated by Django 4.2.4 on 2023-08-16 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restau', '0013_products_imagem_padrao'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='products',
            name='imagem_padrao',
        ),
        migrations.AddField(
            model_name='frontendsetup',
            name='imagem_padrao',
            field=models.ImageField(blank=True, default='default_image.jpg', null=True, upload_to='assets/Products/default/', verbose_name='Imagem Padrão'),
        ),
    ]
