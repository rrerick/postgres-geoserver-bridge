# Generated by Django 4.0.6 on 2022-09-06 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='create_pg_user',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=200)),
                ('password', models.CharField(max_length=200)),
                ('dbname', models.CharField(max_length=200)),
                ('ip', models.CharField(max_length=100)),
                ('port', models.CharField(max_length=10)),
            ],
            options={
                'verbose_name': 'Create Database information',
            },
        ),
        migrations.CreateModel(
            name='Pg_User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=200)),
                ('pub_key', models.CharField(blank=True, max_length=500)),
                ('token', models.CharField(blank=True, max_length=300)),
                ('dbname', models.CharField(max_length=200)),
                ('ip', models.CharField(max_length=100)),
                ('port', models.CharField(max_length=10)),
            ],
            options={
                'verbose_name': 'Pg_User',
            },
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.CharField(max_length=200)),
                ('user', models.CharField(max_length=300)),
                ('token', models.CharField(max_length=500)),
                ('pub_key', models.CharField(max_length=500)),
            ],
            options={
                'verbose_name': "Geoserver's User",
            },
        ),
        migrations.CreateModel(
            name='UsersGeoserver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('geoserver_ip', models.CharField(max_length=200)),
                ('geoserver_user', models.CharField(max_length=50)),
                ('geoserver_password', models.CharField(max_length=200)),
                ('key', models.CharField(blank=True, max_length=500)),
                ('pub_key', models.CharField(blank=True, max_length=500)),
            ],
            options={
                'verbose_name': "Create Geoserve's User",
            },
        ),
    ]