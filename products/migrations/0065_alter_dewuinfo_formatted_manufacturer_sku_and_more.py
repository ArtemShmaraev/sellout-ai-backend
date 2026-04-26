
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0064_product_formatted_manufacturer_sku_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dewuinfo',
            name='formatted_manufacturer_sku',
            field=models.CharField(db_index=True, default='', max_length=128),
        ),
        migrations.AlterField(
            model_name='product',
            name='formatted_manufacturer_sku',
            field=models.CharField(db_index=True, default='', max_length=128),
        ),
        migrations.AlterField(
            model_name='sginfo',
            name='formatted_manufacturer_sku',
            field=models.CharField(db_index=True, default='', max_length=128),
        ),
    ]
