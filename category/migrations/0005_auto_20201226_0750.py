# Generated by Django 3.1.3 on 2020-12-26 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0004_auto_20201224_0739'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='remainder',
            field=models.BooleanField(default=True, help_text='Check if pot of money.'),
        ),
    ]
