# Generated by Django 3.0.2 on 2020-05-02 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_profile_profile_pic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profile_pic',
            field=models.ImageField(default='accounts/profile_pics/def.png', upload_to='accounts/profile_pics'),
        ),
    ]
