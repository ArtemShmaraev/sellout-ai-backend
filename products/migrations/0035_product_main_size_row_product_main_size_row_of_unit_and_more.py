
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0034_alter_dewuinfo_processed_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='main_size_row',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='main_size_row_of_unit',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='unit_common_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
