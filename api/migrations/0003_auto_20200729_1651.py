# Generated by Django 3.0.2 on 2020-07-29 16:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0002_auto_20200129_2017"),
    ]

    operations = [
        migrations.RenameField(
            model_name="returns",
            old_name="inflation",
            new_name="bill_rate",
        ),
        migrations.RemoveField(
            model_name="returns",
            name="ltrate",
        ),
        migrations.RemoveField(
            model_name="returns",
            name="real_bond_tr",
        ),
        migrations.RemoveField(
            model_name="returns",
            name="real_eq_tr",
        ),
        migrations.RemoveField(
            model_name="returns",
            name="stir",
        ),
    ]
