
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0024_product_parameters'),
    ]

    operations = [
        migrations.CreateModel(
            name='RansomRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=128)),
                ('tg_name', models.CharField(default='', max_length=128)),
                ('phone_number', models.CharField(default='', max_length=64)),
                ('email', models.CharField(default='', max_length=128)),
                ('url', models.CharField(default='', max_length=512)),
                ('photo', models.CharField(default='', max_length=128)),
                ('info', models.CharField(default='', max_length=1024)),
            ],
        ),
    ]
