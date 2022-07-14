# Generated by Django 4.0.6 on 2022-07-14 17:20

import core.validators
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('name', models.CharField(max_length=200, primary_key=True, serialize=False, unique=True)),
            ],
            options={
                'verbose_name_plural': 'categories',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=50)),
                ('price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('description', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('province', models.CharField(choices=[('Lower Silesia', 'Lower Silesia'), ('Kuyavia-Pomerania', 'Kuyavia-Pomerania'), ('Lodzkie', 'Lodzkie'), ('Lublin', 'Lublin'), ('Lubusz', 'Lubusz'), ('Lesser Poland', 'Lesser Poland'), ('Masovia', 'Masovia'), ('Subcarpathia', 'Subcarpathia'), ('Pomerania', 'Pomerania'), ('Silesia', 'Silesia'), ('Warmia-Masuria', 'Warmia-Masuria'), ('Greater Poland', 'Greater Poland'), ('West Pomerania', 'West Pomerania')], max_length=64)),
                ('phone_number', models.CharField(max_length=9, validators=[core.validators.validate_phone_number])),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to=settings.AUTH_USER_MODEL)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='core.category')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
    ]
