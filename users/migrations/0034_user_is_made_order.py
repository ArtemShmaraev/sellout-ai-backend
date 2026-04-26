
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0033_alter_user_referral_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_made_order',
            field=models.BooleanField(default=False),
        ),
    ]
