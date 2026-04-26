
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0092_alter_product_score_product_page'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_recommend',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
