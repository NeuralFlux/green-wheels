# Generated by Django 2.1.2 on 2018-11-08 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Eprint_users', '0008_printdocs_collected'),
    ]

    operations = [
        migrations.AddField(
            model_name='printdocs',
            name='is_confirmed',
            field=models.BooleanField(default=False),
        ),
    ]