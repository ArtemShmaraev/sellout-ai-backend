
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_shoppingcart_bonus_sale'),
    ]

    operations = [
        migrations.AddField(
            model_name='shoppingcart',
            name='promo_sale',
            field=models.IntegerField(default=0),
        ),
    ]
