

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20190630_1408'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='owner',
            field=models.CharField(choices=[('A', 'All'), ('M', 'Man'), ('W', 'Women')], default='A', max_length=1),
        ),
        migrations.AlterField(
            model_name='item',
            name='category',
            field=models.CharField(choices=[('all', 'Все'), ('high_boots', 'Сапоги'), ('boots', 'Ботинки'), ('half_boots', 'П/ботинки'), ('shoes', 'Туфли'), ('summer_shoes', 'Туфли летние'), ('home_shoes', 'Домашняя обувь'), ('sport_shoes', 'Обувь для активного отдыха')], max_length=26),
        ),
    ]
