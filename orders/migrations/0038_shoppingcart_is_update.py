
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0037_alter_order_pvz_alter_order_pvz_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='shoppingcart',
            name='is_update',
            field=models.BooleanField(default=False),
        ),
    ]
