# Generated by Django 4.2.3 on 2023-07-21 18:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restau', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='produts',
            name='image',
            field=models.ImageField(blank=True, default='default_image.jpg', null=True, upload_to='assets/Products/'),
        ),
    ]
