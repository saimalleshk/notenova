# Generated by Django 5.1.4 on 2025-01-13 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appnotenova', '0005_alter_timetracker_aux_used_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timetracker',
            name='aux_used',
            field=models.CharField(choices=[('timeout', 'TimeOut'), ('Other', 'Other'), ('training', 'Training'), ('Mentoring', 'DEP')], max_length=20),
        ),
    ]
