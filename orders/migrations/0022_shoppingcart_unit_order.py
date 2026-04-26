
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0021_rename_tel_order_phone_order_delivery_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='shoppingcart',
            name='unit_order',
            field=models.JSONField(default=list),
        ),
    ]
