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

        all_data = json.load(open("lines.json", encoding="utf-8"))
        s = flatten_lines(all_data)
        for line in s:
            if Line.objects.filter(name=line['name']).exists():
                continue
            else:
                db_line = Line(name=line['name'], full_name=line['name'])
                db_line.save()
                if line['parent']:
                    db_line.parent_line = Line.objects.get(name=line['parent'])
                db_line.save()
        print('finished')
