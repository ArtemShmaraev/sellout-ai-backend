
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0030_product_another_configuration_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sizetranslationrows',
            name='table',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rows', to='products.sizetable'),
        ),
    ]
