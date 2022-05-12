

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20210520_1929'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='sub_images',
            field=models.OneToOneField(blank=True, null=True, on_delete='SET_NULL', to='core.SubImage', verbose_name='Дополнительные картинки'),
        ),
    ]
