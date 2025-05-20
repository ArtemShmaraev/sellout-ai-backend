from itertools import count

from django.core import signing
from django.core.management.base import BaseCommand
import json
from products.models import Product, Category, Line, Gender, Brand, Tag, Collection, Color, SizeRow, Collab
from django.core.exceptions import ObjectDoesNotExist

from users.models import User, EmailConfirmation


class Command(BaseCommand):

    def handle(self, *args, **options):
        users = User.objects.all()
        for new_user in users:
            email_confirmation = EmailConfirmation(user=new_user)
            email_confirmation.token = signing.dumps(new_user.email)
            email_confirmation.save()
            print(f"http://127.0.0.1:8000/email_confirmated/{email_confirmation.token}")


