def build_category_tree(categories):
    category_dict = {}
    root_categories = []

    # Создаем словарь для быстрого доступа к категориям по их идентификатору
    for category in categories:
        category_dict[category["id"]] = category

    # Строим иерархическую структуру категорий
    for category in categories:
        parent_ids = category["parent_category"]
        if parent_ids:
            parent_category = category_dict[parent_ids]
            parent_category.setdefault("children", []).append(category)
        else:
            root_categories.append(category)
    return root_categories


def category_no_child(cats):
    result = []
    for cat in cats:
        if 'subcategories' not in cat:
            result.append(cat)
        else:
            children = cat['subcategories']
            result.extend(category_no_child(children))
    # result.sort(key=lambda x: x['full_name'])
    return result



def build_line_tree(lines):
    line_dict = {}
    root_lines = []

    # Создание словаря линеек с использованием их идентификаторов в качестве ключей
    for line in lines:
        line_dict[line['id']] = line

    # Построение дерева линеек
    for line in lines:
        parent_line = line['parent_line']
        if parent_line is None:
            # Если у линейки нет родительской линейки, она считается корневой линейкой
            root_lines.append(line)
        else:
            parent_id = parent_line['id']
            parent_line = line_dict.get(parent_id)
            if parent_line:
                # Если родительская линейка найдена, добавляем текущую линейку в список её дочерних линеек
                parent_line.setdefault('children', []).append(line)

    def sort_children(data):
        order = {'low': 0, 'mid': 1, 'high': 2, "air jordan 1": 3,
                 "air jordan 2": 4, "air jordan 3": 5, "air jordan 4": 6,
                 "air jordan 5": 7, "air jordan 6": 8, "air jordan 7": 9,
                 "air jordan 8": 10, "air jordan 9": 11, "air jordan 10": 12,
                 "air jordan 11": 13, "air jordan 12": 14, "air jordan 13": 15,
                 "air jordan 14": 16, "air jordan 15": 17}

        def sort_key(child):
            name = child['name'].lower()
            if 'все' in name:
                return 0, '', ''
            elif name.isdigit():
                return (1, int(name), '')
            return 1, order.get(name, float('inf')), name

        for item in data:
            children = item.get('children')
            if children:
                item['children'] = sorted(children, key=sort_key)
                sort_children(item['children'])
        return data

    root_lines = sort_children(root_lines)
    with_children = [x for x in root_lines if x.get('children')]
    without_children = [x for x in root_lines if not x.get('children')]

    sorted_data_with_children = sorted(with_children, key=lambda x: x['name'].lower())

    # Сортируем оставшиеся элементы
    sorted_data_without_children = sorted(without_children, key=lambda x: x['name'].lower())
    # Объединяем отсортированные части
    sorted_data = sorted_data_with_children + sorted_data_without_children

    return sorted_data



def line_no_child(lines):
    line_dict = {}
    root_lines = []

    # Создание словаря линеек с использованием их идентификаторов в качестве ключей
    for line in lines:
        line_dict[line['id']] = line

    # Построение дерева линеек
    for line in lines:
        parent_line = line['parent_line']
        if parent_line is None:
            # Если у линейки нет родительской линейки, она считается корневой линейкой
            root_lines.append(line)
        else:
            parent_id = parent_line['id']
            parent_line = line_dict.get(parent_id)
            if parent_line:
                # Если родительская линейка найдена, добавляем текущую линейку в список её дочерних линеек
                parent_line.setdefault('children', []).append(line)

    def get_lines_without_children(lines):
        result = []
        for line in lines:
            if 'children' not in line:
                result.append(line)
            else:
                children = line['children']
                result.extend(get_lines_without_children(children))
        result.sort(key=lambda x: x['full_name'])
        return result

    return get_lines_without_children(root_lines)


