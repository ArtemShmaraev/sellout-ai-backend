
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0041_order_total_bonus'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='invoice_data',
            field=models.JSONField(default=dict),
        ),
    ]
