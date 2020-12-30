# Generated by Django 2.2.10 on 2020-12-30 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('theories', '0003_auto_20201229_2000'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='opiniondependency',
            options={'ordering': ['-rank'], 'verbose_name': 'Opinion Dependency', 'verbose_name_plural': 'Opinion Dependencies'},
        ),
        migrations.AlterModelOptions(
            name='statsdependency',
            options={'ordering': ['-rank'], 'verbose_name': 'Stats Dependency', 'verbose_name_plural': 'Stats Dependency'},
        ),
        migrations.AddField(
            model_name='opiniondependency',
            name='rank',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='statsdependency',
            name='rank',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='statsflatdependency',
            name='rank',
            field=models.FloatField(default=0.0),
        ),
    ]
