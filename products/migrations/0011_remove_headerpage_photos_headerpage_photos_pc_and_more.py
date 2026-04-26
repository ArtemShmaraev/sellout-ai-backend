
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0010_headerpage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='headerpage',
            name='photos',
        ),
        migrations.AddField(
            model_name='headerpage',
            name='photos_pc',
            field=models.ManyToManyField(blank=True, related_name='headers_pc', to='products.photo'),
        ),
        migrations.AddField(
            model_name='headerpage',
            name='photos_phone',
            field=models.ManyToManyField(blank=True, related_name='headers_photos', to='products.photo'),
        ),
    ]
