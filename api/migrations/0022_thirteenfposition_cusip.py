# Generated by Django 3.0.8 on 2021-11-12 20:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0021_thirteenfposition"),
    ]

    operations = [
        migrations.AddField(
            model_name="thirteenfposition",
            name="cusip",
            field=models.CharField(default="", max_length=10),
            preserve_default=False,
        ),
    ]