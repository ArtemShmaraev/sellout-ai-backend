
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0050_product_one_update_alter_photo_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='parse_price',
            field=models.BooleanField(default=False),
        ),
    ]
