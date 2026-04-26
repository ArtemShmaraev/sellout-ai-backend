
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0053_alter_order_cancel_reason_alter_order_comment_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='shoppingcart',
            name='delivery_info',
            field=models.JSONField(default=dict),
        ),
    ]
