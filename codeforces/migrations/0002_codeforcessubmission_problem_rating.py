# Generated by Django 5.0.7 on 2024-07-17 02:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('codeforces', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='codeforcessubmission',
            name='problem_rating',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
