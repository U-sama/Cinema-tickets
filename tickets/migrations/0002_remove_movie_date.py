# Generated by Django 4.1.5 on 2023-01-08 20:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("tickets", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(model_name="movie", name="date",),
    ]