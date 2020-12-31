# Generated by Django 3.1.3 on 2020-12-22 18:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0002_auto_20201222_1238'),
        ('budget', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AvgQuarterBudget',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('remainder', models.BooleanField(default=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='category.category')),
                ('categorygroup', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='category.categorygroup')),
            ],
        ),
    ]
