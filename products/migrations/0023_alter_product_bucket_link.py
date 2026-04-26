
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0022_alter_product_colorway_alter_product_model'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='bucket_link',
            field=models.ManyToManyField(blank=True, db_index=True, null=True, related_name='product', to='products.photo'),
        ),
    ]
