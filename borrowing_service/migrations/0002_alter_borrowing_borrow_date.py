# Generated by Django 5.0.7 on 2024-08-05 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("borrowing_service", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="borrowing",
            name="borrow_date",
            field=models.DateField(auto_now_add=True),
        ),
    ]