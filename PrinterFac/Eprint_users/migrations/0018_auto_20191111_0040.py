# Generated by Django 2.1.3 on 2019-11-10 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Eprint_users', '0017_auto_20191110_2209'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustSearch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pickup_loc', models.CharField(default='', max_length=25)),
                ('drop_loc', models.CharField(default='', max_length=25)),
                ('AC_pref', models.BooleanField(default=False)),
                ('seats_req', models.IntegerField(default=1)),
                ('start_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'CustSearch',
            },
        ),
        migrations.AddField(
            model_name='profile',
            name='aadhar_num',
            field=models.CharField(default='', max_length=12),
        ),
        migrations.AddField(
            model_name='profile',
            name='aadhar_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='license_num',
            field=models.CharField(default='', max_length=15),
        ),
        migrations.AddField(
            model_name='profile',
            name='license_verified',
            field=models.BooleanField(default=False),
        ),
    ]
