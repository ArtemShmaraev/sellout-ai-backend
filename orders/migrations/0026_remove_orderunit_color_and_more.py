
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0025_order_delivery_price_order_groups_delivery_order_pvz_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderunit',
            name='color',
        ),
        migrations.RemoveField(
            model_name='orderunit',
            name='configuration',
        ),
    ]
