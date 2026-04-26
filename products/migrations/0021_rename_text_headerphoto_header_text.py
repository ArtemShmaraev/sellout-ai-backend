
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0020_headerphoto_text'),
    ]

    operations = [
        migrations.RenameField(
            model_name='headerphoto',
            old_name='text',
            new_name='header_text',
        ),
    ]
