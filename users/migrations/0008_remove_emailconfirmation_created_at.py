
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_user_verify_email_emailconfirmation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emailconfirmation',
            name='created_at',
        ),
    ]
