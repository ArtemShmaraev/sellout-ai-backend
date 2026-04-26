
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0035_alter_user_referral_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='referral_data',
            field=models.JSONField(default=dict),
        ),
    ]
