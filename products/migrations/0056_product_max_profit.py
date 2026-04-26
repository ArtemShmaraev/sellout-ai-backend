
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0055_product_category_id_product_category_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='max_profit',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
