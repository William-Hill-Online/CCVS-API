# Generated by Django 3.0.1 on 2020-01-14 15:02
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('container_scanning', '0005_job'),
    ]

    operations = [
        migrations.AlterUniqueTogether(name='imagevendor', unique_together=None,),
        migrations.RemoveField(model_name='imagevendor', name='image',),
        migrations.RemoveField(model_name='imagevendor', name='vendor',),
        migrations.RemoveField(model_name='job', name='type',),
        migrations.DeleteModel(name='Image',),
        migrations.DeleteModel(name='ImageVendor',),
    ]