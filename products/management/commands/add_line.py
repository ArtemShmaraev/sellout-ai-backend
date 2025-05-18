from itertools import count
from django.core.management.base import BaseCommand
import json
from products.models import Product, Category, Line, Gender, Brand, Tag, Collection, Color, Collab
from django.core.exceptions import ObjectDoesNotExist
import users.models


class Command(BaseCommand):

    def handle(self, *args, **options):

        def flatten_lines(lines_list, parent_name=None):
            result = []
            for line in lines_list:
                name = line["name"]
                result.append({"name": name, "parent": parent_name})
                if line["children"]:
                    result.extend(flatten_lines(line["children"], parent_name=name))
            return result

        all_data = json.load(open("line2.json", encoding="utf-8"))
        s = flatten_lines(all_data)
        for line in s:
            db_line = Line.objects.get_or_create(name=line['name'])[0]
            db_line.save()
            if line['parent']:
                db_line.parent_line = Line.objects.get(name=line['parent'])
            db_line.save()
        brands = all_data
        for brand in brands:
            if Brand.objects.filter(name=brand['name']).exists():
                continue
            else:
                db_brand = Brand.objects.get_or_create(name=brand['name'])[0]
                db_brand.save()
        print('finished')
