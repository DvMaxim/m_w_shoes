

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20210518_1622'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='owner',
            field=models.CharField(choices=[('A', 'All'), ('M', 'Man'), ('W', 'Woman'), ('U', 'Unisex')], default='A', max_length=1),
        ),
    ]
