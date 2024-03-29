# Generated by Django 4.1.5 on 2023-01-06 01:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('category', '0005_auto_20201226_0750'),
    ]

    operations = [
        migrations.CreateModel(
            name='Envelope',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=8)),
                ('date', models.DateField()),
                ('plus_minus', models.DecimalField(decimal_places=2, max_digits=8)),
                ('carryover', models.DecimalField(decimal_places=2, max_digits=8)),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='category.category')),
                ('categorygroup', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='category.categorygroup')),
            ],
        ),
    ]
