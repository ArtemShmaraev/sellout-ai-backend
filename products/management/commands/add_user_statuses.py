import json
from django.core.management.base import BaseCommand
from products.models import Color
from users.models import User, UserStatus


class Command(BaseCommand):
    help = 'Fill Color model with data from a JSON file'

    def handle(self, *args, **kwargs):
        penis = UserStatus(name="Penis", total_orders_amount=0, start_bonuses=True, birthday_gift=True,
                              unit_max_bonuses=0,
                              free_ship_amount=0,
                              exclusive_sale=False,
                              close_release=False, priority_service=False, percentage_bonuses=10, base=False)
        penis.save()
        # amethyst = UserStatus(name="Amethyst", total_orders_amount=0, start_bonuses=True, birthday_gift=True, unit_max_bonuses=250,
        #                       free_ship_amount=20000,
        #                       exclusive_sale=False,
        #                       close_release=False, priority_service=False, percentage_bonuses=10)
        # amethyst.save()
        #
        # sapphire = UserStatus(name="Supphire", total_orders_amount=15000, start_bonuses=True, birthday_gift=True, unit_max_bonuses=500,
        #                       free_ship_amount=20000,
        #                       exclusive_sale=False,
        #                       close_release=False, priority_service=False, percentage_bonuses=15)
        # sapphire.save()
        #
        # emerald = UserStatus(name="Emerald", total_orders_amount=45000, start_bonuses=True, birthday_gift=True, unit_max_bonuses=750,
        #                      free_ship_amount=15000,
        #                      exclusive_sale=False,
        #                      close_release=False, priority_service=False, percentage_bonuses=20)
        # emerald.save()
        #
        # ruby = UserStatus(name="Ruby", total_orders_amount=100000,start_bonuses=True, birthday_gift=True, unit_max_bonuses=1000,
        #                   free_ship_amount=15000,
        #                   exclusive_sale=True,
        #                   close_release=False, priority_service=False, percentage_bonuses=25)
        # ruby.save()
        #
        # diamond = UserStatus(name="Diamond", total_orders_amount=300000, start_bonuses=True, birthday_gift=True, unit_max_bonuses=1500,
        #                      free_ship_amount=15000,
        #                      exclusive_sale=True,
        #                      close_release=True, priority_service=True, percentage_bonuses=30)
        # diamond.save()
        #
        # privileged = UserStatus(name="Privileged", start_bonuses=False, birthday_gift=False, unit_max_bonuses=0,
        #                         free_ship_amount=0,
        #                         exclusive_sale=True,
        #                         close_release=True, priority_service=True, base=False, percentage_bonuses=0)
        # privileged.save()
        #
        # f_and_f = UserStatus(name="Friends & Family", start_bonuses=False, birthday_gift=False, unit_max_bonuses=0,
        #                      free_ship_amount=0,
        #                      exclusive_sale=True,
        #                      close_release=True, priority_service=True, base=False, percentage_bonuses=0)
        # f_and_f.save()

