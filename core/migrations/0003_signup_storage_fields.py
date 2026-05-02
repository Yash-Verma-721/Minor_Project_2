from django.db import migrations, models

MB = 1024 * 1024


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_sharedlink"),
    ]

    operations = [
        migrations.AddField(
            model_name="signup",
            name="storage_used",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="signup",
            name="storage_limit",
            field=models.IntegerField(default=300 * MB),
        ),
    ]
