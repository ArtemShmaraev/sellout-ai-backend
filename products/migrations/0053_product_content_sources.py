
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0052_remove_product_parse_price_product_last_parse_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='content_sources',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
    ]
