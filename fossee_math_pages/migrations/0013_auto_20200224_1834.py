# Generated by Django 2.2.7 on 2020-02-24 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fossee_math_pages', '0012_auto_20200224_1827'),
    ]

    operations = [
        migrations.AlterField(
            model_name='data',
            name='data_image',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
    ]