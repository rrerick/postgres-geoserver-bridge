# Generated by Django 4.0.6 on 2023-01-03 18:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Metadata',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_name', models.CharField(max_length=200)),
                ('schema_name', models.CharField(max_length=200)),
                ('geoserver_title', models.CharField(default='null', max_length=200)),
                ('geoserver_style_uri', models.CharField(default='null', max_length=200)),
                ('geoserver_workspace', models.CharField(default='null', max_length=200)),
                ('geoserver_ip', models.CharField(default='null', max_length=200)),
                ('style_name', models.CharField(default='st_with_no_name', max_length=200)),
                ('data_insercao', models.DateField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'metadado',
                'db_table': 'tb_metadata_geoserver',
            },
        ),
        migrations.CreateModel(
            name='Workspaces',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('geoserver_workspace', models.CharField(default='null', max_length=200)),
                ('geoserver_ip', models.CharField(default='null', max_length=200)),
                ('data_insercao', models.DateField(auto_now_add=True)),
            ],
            options={
                'db_table': 'tb_geoserver_workspces',
            },
        ),
        migrations.CreateModel(
            name='Style',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('geoserver_style', models.CharField(default='null', max_length=300)),
                ('style_name', models.CharField(default='null', max_length=300)),
                ('data_insercao', models.DateField(auto_now_add=True)),
                ('geoserver_workspace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pool.workspaces')),
            ],
            options={
                'db_table': 'tb_geoserver_style',
            },
        ),
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('geoserver_store', models.CharField(default='null', max_length=200)),
                ('data_insercao', models.DateField(auto_now_add=True)),
                ('geoserver_workspace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pool.workspaces')),
            ],
            options={
                'verbose_name': 'store',
                'db_table': 'tb_geoserver_datastore',
            },
        ),
    ]
