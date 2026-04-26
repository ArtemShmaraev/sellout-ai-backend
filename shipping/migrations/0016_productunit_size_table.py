
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0037_alter_product_rel_num'),
        ('shipping', '0015_remove_productunit_color_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='productunit',
            name='size_table',
            field=models.ManyToManyField(blank=True, null=True, related_name='product_units', to='products.sizetable'),
        ),
    ]
