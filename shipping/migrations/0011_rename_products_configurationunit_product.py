
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0010_configurationunit'),
    ]

    operations = [
        migrations.RenameField(
            model_name='configurationunit',
            old_name='products',
            new_name='product',
        ),
    ]
