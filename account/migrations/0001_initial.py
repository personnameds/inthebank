# Generated by Django 3.1.4 on 2021-02-07 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('balance', models.DecimalField(blank=True, decimal_places=2, max_digits=8)),
                ('last_update', models.DateField(blank=True)),
                ('is_creditcard', models.BooleanField(default=False)),
            ],
        ),
    ]
