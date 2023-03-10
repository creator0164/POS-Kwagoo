# Generated by Django 4.0.1 on 2023-01-23 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posApp', '0004_salesitems'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('user_type', models.CharField(blank=True, max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
