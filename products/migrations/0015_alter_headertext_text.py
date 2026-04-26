
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0014_alter_headerphoto_collabs_alter_headertext_collabs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='headertext',
            name='text',
            field=models.CharField(default='', max_length=2048),
        ),
    ]
