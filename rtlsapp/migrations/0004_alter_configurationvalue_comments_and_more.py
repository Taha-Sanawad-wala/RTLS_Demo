# Generated by Django 4.2.6 on 2023-10-31 07:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rtlsapp', '0003_alter_configurationvalue_workcenter'),
    ]

    operations = [
        migrations.AlterField(
            model_name='configurationvalue',
            name='comments',
            field=models.CharField(max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='configurationvalue',
            name='confgObject',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='configurationvalue',
            name='plant',
            field=models.CharField(max_length=4, null=True),
        ),
    ]
