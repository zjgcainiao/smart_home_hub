# Generated by Django 2.1.5 on 2019-02-21 06:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('philips_hue', '0002_auto_20190220_2156'),
    ]

    operations = [
        migrations.AddField(
            model_name='monitorbridge',
            name='bridge_unique_id',
            field=models.CharField(max_length=120, null=True),
        ),
    ]
