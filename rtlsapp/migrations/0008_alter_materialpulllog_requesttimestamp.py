# Generated by Django 4.2.6 on 2023-11-01 08:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rtlsapp', '0007_alter_configurationvalue_configurationvalueid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='materialpulllog',
            name='requestTimeStamp',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
