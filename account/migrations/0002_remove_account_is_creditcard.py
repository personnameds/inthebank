# Generated by Django 3.1.4 on 2021-02-07 14:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='is_creditcard',
        ),
    ]