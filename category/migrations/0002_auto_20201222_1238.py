# Generated by Django 3.1.3 on 2020-12-22 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='budget_method',
            field=models.CharField(choices=[('N', 'None'), ('C', 'Constant Month to Month'), ('A', 'Average over last 3 months'), ('S', 'Scheduled Transactions'), ('Y', 'Based on Last Year')], default='N', max_length=1),
        ),
        migrations.AlterField(
            model_name='categorygroup',
            name='budget_method',
            field=models.CharField(choices=[('N', 'None'), ('C', 'Constant Month to Month'), ('A', 'Average over last 3 months'), ('S', 'Scheduled Transactions'), ('Y', 'Based on Last Year')], default='N', max_length=1),
        ),
    ]
