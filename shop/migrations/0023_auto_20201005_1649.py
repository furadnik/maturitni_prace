# Generated by Django 3.1 on 2020-10-05 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0022_auto_20200731_1511'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='items',
            field=models.ManyToManyField(related_name='categories', to='shop.Item'),
        ),
    ]