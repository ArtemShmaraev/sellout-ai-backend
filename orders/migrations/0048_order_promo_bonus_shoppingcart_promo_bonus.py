
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0047_order_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='promo_bonus',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='shoppingcart',
            name='promo_bonus',
            field=models.IntegerField(default=0),
        ),
    ]
