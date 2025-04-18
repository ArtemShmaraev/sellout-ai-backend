from django.db import transaction

@transaction.atomic
def fill_missing_descriptions_line(line):
    description = Description.objects.filter(line=line).first()
    if not description:
        parent_line = line.parent_line
        if parent_line:
            parent_description = fill_missing_descriptions_line(parent_line)
            if parent_description:
                description = Description(line=line, category=None, description=parent_description.description)
                description.save()
    return description

@transaction.atomic
def fill_missing_descriptions_category(category):
    description = Description.objects.filter(category=category).first()
    if not description:
        parent_category = category.parent_category
        if parent_category:
            parent_description = fill_missing_descriptions_category(parent_category)
            if parent_description:
                description = Description(line=None, category=category, description=parent_description.description)
                description.save()
    return description

def fill_missing_descriptions_recursive():
    lines_without_description = Line.objects.filter(subline__isnull=True)  # Получаем линейки без подлинеек

    for line in lines_without_description:
        fill_missing_descriptions_line(line)
        categories_without_description = line.category_set.filter(subcat__isnull=True)  # Получаем категории без подкатегорий для текущей линейки

        for category in categories_without_description:
            fill_missing_descriptions_category(category)
