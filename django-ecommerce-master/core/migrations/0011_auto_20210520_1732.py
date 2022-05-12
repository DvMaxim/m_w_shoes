

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_remove_item_label'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_1', models.ImageField(null=True, upload_to='')),
                ('image_2', models.ImageField(null=True, upload_to='')),
                ('image_3', models.ImageField(null=True, upload_to='')),
                ('image_4', models.ImageField(null=True, upload_to='')),
            ],
        ),
        migrations.AddField(
            model_name='item',
            name='sub_images',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.SubImage',
                                       verbose_name='Дополнительные картинки'),
        ),
    ]
