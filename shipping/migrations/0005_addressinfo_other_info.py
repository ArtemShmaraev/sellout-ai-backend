
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0004_alter_productunit_size'),
    ]

    operations = [
        migrations.AddField(
            model_name='addressinfo',
            name='other_info',
            field=models.JSONField(default=dict),
        ),
    ]
