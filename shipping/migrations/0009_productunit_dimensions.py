
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0008_rename_good_size_platform_productunit_view_size_platform_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='productunit',
            name='dimensions',
            field=models.JSONField(default=dict),
        ),
    ]
