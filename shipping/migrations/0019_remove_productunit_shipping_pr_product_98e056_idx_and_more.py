
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0018_alter_productunit_unique_together_and_more'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='productunit',
            name='shipping_pr_product_98e056_idx',
        ),
        migrations.AlterUniqueTogether(
            name='productunit',
            unique_together=set(),
        ),
    ]
