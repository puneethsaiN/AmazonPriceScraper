# Generated by Django 5.0.1 on 2024-01-07 10:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp1', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='dateAdded',
        ),
        migrations.RemoveField(
            model_name='product',
            name='price',
        ),
        migrations.RemoveField(
            model_name='product',
            name='priceChange',
        ),
        migrations.CreateModel(
            name='ProductHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField()),
                ('priceChange', models.FloatField()),
                ('dateAdded', models.DateField()),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp1.product')),
            ],
        ),
    ]