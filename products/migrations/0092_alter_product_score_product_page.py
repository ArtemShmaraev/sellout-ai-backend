
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0091_remove_category_up_score_product_up_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='score_product_page',
            field=models.IntegerField(db_index=True, default=0),
        ),
    ]
