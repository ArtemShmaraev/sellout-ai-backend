
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0058_product_products_pr_id_b46934_idx_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gender',
            name='name',
            field=models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('K', 'Kids')], db_index=True, max_length=255),
        ),
    ]
