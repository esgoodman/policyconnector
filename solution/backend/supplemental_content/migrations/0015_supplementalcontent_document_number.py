# Generated by Django 3.2.12 on 2022-04-22 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supplemental_content', '0014_supplementalcontent_docket_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplementalcontent',
            name='document_number',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
