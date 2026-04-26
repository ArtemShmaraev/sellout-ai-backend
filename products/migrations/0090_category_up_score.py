
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0089_alter_product_is_new'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='up_score',
            field=models.BooleanField(default=False),
        ),
    ]
