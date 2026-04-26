
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0027_orderunit_weight'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery_view_price',
            field=models.IntegerField(default=0),
        ),
    ]
