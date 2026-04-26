
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0048_order_promo_bonus_shoppingcart_promo_bonus'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='is_finish',
            field=models.BooleanField(default=False),
        ),
    ]
