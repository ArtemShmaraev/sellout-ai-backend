
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0030_alter_order_status_alter_orderunit_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='sale',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='shoppingcart',
            name='sale',
            field=models.IntegerField(default=0),
        ),
    ]
