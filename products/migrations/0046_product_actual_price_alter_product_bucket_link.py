
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0045_product_in_sg'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='actual_price',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='bucket_link',
            field=models.ManyToManyField(blank=True, db_index=True, related_name='product', to='products.photo'),
        ),
    ]
