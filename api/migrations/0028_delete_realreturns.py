# Generated by Django 4.0.4 on 2022-06-11 01:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0027_alter_coverage_unique_together"),
    ]

    operations = [
        migrations.DeleteModel(
            name="RealReturns",
        ),
    ]
