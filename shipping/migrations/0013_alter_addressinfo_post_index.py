
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0012_deliverytype_days'),
    ]

    operations = [
        migrations.AlterField(
            model_name='addressinfo',
            name='post_index',
            field=models.CharField(default=0, max_length=10),
        ),
    ]
