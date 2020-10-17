# Generated by Django 3.0.2 on 2020-09-03 22:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0011_coverage_security_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="coverage",
            name="currency",
            field=models.CharField(max_length=5, null=True),
        ),
        migrations.AlterField(
            model_name="coverage",
            name="issuer",
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name="coverage",
            name="ticker",
            field=models.CharField(max_length=10, null=True),
        ),
    ]
