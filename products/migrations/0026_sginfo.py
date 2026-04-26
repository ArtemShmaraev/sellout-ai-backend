
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0025_ransomrequest'),
    ]

    operations = [
        migrations.CreateModel(
            name='SGInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('manufacturer_sku', models.CharField(default='', max_length=256)),
                ('data', models.JSONField(default=dict)),
            ],
        ),
    ]
