# Generated by Django 2.1.2 on 2018-10-18 14:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Eprint_users', '0002_auto_20181018_1958'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='user',
        ),
        migrations.DeleteModel(
            name='Profile',
        ),
    ]
