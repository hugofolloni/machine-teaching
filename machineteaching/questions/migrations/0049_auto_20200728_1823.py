# Generated by Django 2.2.5 on 2020-07-28 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0048_onlineclass_chapters'),
    ]

    operations = [
        migrations.AddField(
            model_name='onlineclass',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='professor',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
