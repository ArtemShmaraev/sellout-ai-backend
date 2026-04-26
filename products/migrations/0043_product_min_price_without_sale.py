
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0042_product_is_sale_product_percentage_sale'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='min_price_without_sale',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
