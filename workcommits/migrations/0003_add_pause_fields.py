from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("workcommits", "0002_add_tag_to_workcommit"),
    ]

    operations = [
        migrations.AddField(
            model_name="workcommit",
            name="paused_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="workcommit",
            name="total_paused_seconds",
            field=models.IntegerField(default=0),
        ),
    ]
