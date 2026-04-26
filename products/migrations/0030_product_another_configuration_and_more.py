
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0029_product_property_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='another_configuration',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='similar_product',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
    ]
