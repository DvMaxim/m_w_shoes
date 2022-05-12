# Generated by Django 2.2.14 on 2021-05-24 06:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='contact_email',
            field=models.CharField(default='Some user email', max_length=1000),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='contact_letter',
            field=models.CharField(default='Some user message', max_length=1000),
        ),
    ]
