# Generated by Django 2.1.3 on 2018-12-01 23:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Eprint_users', '0013_auto_20181202_0430'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='image',
        ),
    ]