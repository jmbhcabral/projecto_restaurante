# Generated by Django 4.2.3 on 2023-07-18 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('site_setup', '0002_delete_menulinkadmin'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteSetup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=65)),
                ('description', models.CharField(max_length=255)),
                ('show_header', models.BooleanField(default=True)),
                ('show_search', models.BooleanField(default=True)),
                ('show_menu', models.BooleanField(default=True)),
                ('show_description', models.BooleanField(default=True)),
                ('show_pagination', models.BooleanField(default=True)),
                ('show_footer', models.BooleanField(default=True)),
                ('show_reservations', models.BooleanField(default=True)),
                ('show_takeaway', models.BooleanField(default=True)),
                ('show_delivery', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Setup',
                'verbose_name_plural': 'Setup',
            },
        ),
    ]
