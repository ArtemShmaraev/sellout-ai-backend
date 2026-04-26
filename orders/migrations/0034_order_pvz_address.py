
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0033_alter_order_status_alter_orderunit_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='pvz_address',
            field=models.CharField(default='', max_length=2048),
        ),
    ]
