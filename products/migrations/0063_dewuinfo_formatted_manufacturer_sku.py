
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0062_headerphoto_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='dewuinfo',
            name='formatted_manufacturer_sku',
            field=models.CharField(default='', max_length=128),
        ),
    ]
