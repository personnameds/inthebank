# Generated by Django 4.1.5 on 2023-03-15 12:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0007_alter_category_group'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='remainder',
        ),
        migrations.RemoveField(
            model_name='categorygroup',
            name='remainder',
        ),
    ]
