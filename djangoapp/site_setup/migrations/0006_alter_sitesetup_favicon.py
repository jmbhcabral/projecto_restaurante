# Generated by Django 4.2.3 on 2023-07-19 19:01

from django.db import migrations, models
import utils.model_validators


class Migration(migrations.Migration):

    dependencies = [
        ('site_setup', '0005_sitesetup_favicon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sitesetup',
            name='favicon',
            field=models.ImageField(blank=True, default='', upload_to='assets/favicon/Y%/m%', validators=[utils.model_validators.validate_png]),
        ),
    ]
