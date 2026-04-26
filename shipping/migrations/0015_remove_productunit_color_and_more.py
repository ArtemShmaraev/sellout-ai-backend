
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0014_rename_days_deliverytype_days_max_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productunit',
            name='color',
        ),
        migrations.RemoveField(
            model_name='productunit',
            name='configuration',
        ),
        migrations.AddField(
            model_name='productunit',
            name='platform_info',
            field=models.JSONField(default=dict),
        ),
        migrations.RemoveField(
            model_name='productunit',
            name='size',
        ),
        migrations.AddField(
            model_name='productunit',
            name='size',
            field=models.ManyToManyField(blank=True, null=True, related_name='product_units', to='products.sizetranslationrows'),
        ),
    ]
