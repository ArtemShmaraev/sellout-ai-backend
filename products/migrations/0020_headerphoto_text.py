
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0019_remove_product_dewu_info'),
    ]

    operations = [
        migrations.AddField(
            model_name='headerphoto',
            name='text',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='headers_photo', to='products.headertext'),
        ),
    ]
