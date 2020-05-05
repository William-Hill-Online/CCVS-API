# Generated by Django 3.0.5 on 2020-05-05 01:00

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('container_scanning', '0011_auto_20200429_2035'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='analysis',
            name='vulnerabilities',
        ),
        migrations.AddField(
            model_name='analysis',
            name='ccvs_results',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='analysis',
            name='errors',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=list),
        ),
        migrations.AlterField(
            model_name='analysis',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'pending'),
                    ('started', 'started'),
                    ('finished', 'finished')
                ],
                default='pending',
                max_length=20
            ),
        ),
    ]
