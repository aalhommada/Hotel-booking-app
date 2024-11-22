# Generated by Django 5.1.3 on 2024-11-15 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="booking",
            name="adults",
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name="booking",
            name="children",
            field=models.PositiveIntegerField(default=0),
        ),
    ]