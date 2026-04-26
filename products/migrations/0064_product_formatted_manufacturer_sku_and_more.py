
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0063_dewuinfo_formatted_manufacturer_sku'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='formatted_manufacturer_sku',
            field=models.CharField(default='', max_length=128),
        ),
        migrations.AddField(
            model_name='sginfo',
            name='formatted_manufacturer_sku',
            field=models.CharField(default='', max_length=128),
        ),
    ]
