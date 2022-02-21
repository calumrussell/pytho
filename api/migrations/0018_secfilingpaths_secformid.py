# Generated by Django 3.0.8 on 2021-07-23 02:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0017_auto_20210406_0222"),
    ]

    operations = [
        migrations.CreateModel(
            name="SecFormId",
            fields=[
                (
                    "form_id",
                    models.SmallIntegerField(primary_key=True, serialize=False),
                ),
                ("form_name", models.CharField(max_length=20)),
            ],
            options={
                "unique_together": {("form_name",)},
            },
        ),
        migrations.CreateModel(
            name="SecFilingPaths",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("issuer_id", models.IntegerField()),
                ("form_id", models.SmallIntegerField()),
                ("date", models.IntegerField()),
                ("path", models.CharField(max_length=20)),
            ],
            options={
                "unique_together": {("issuer_id", "form_id", "date")},
            },
        ),
    ]
