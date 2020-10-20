# Generated by Django 3.0.2 on 2020-08-31 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0008_auto_20200831_1923"),
    ]

    operations = [
        migrations.AddField(
            model_name="fundcoverage",
            name="currency",
            field=models.CharField(default=False, max_length=5),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="fundcoverage",
            name="issuer",
            field=models.CharField(default=False, max_length=200),
            preserve_default=False,
        ),
    ]