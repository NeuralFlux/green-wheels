# Generated by Django 2.1.3 on 2019-11-10 23:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Eprint_users', '0019_auto_20191111_0512'),
    ]

    operations = [
        migrations.AddField(
            model_name='hostsearch',
            name='task_by',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]