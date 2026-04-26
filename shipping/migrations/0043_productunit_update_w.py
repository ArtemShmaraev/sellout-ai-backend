
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0042_productunit_weight_kg'),
    ]

    operations = [
        migrations.AddField(
            model_name='productunit',
            name='update_w',
            field=models.BooleanField(default=False),
        ),
    ]
