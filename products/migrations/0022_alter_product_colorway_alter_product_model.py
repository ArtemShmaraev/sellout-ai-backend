
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0021_rename_text_headerphoto_header_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='colorway',
            field=models.CharField(blank=True, db_index=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='product',
            name='model',
            field=models.CharField(blank=True, db_index=True, max_length=255),
        ),
    ]
