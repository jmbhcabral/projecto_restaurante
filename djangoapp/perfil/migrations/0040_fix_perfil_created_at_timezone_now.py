from __future__ import annotations

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("perfil", "0039_rename_onboarding_min_completed_perfil_onboarding_optional_completed"),
    ]

    operations = [
        migrations.AlterField(
            model_name="perfil",
            name="created_at",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]