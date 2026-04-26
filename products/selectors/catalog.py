from products.models import Brand, Category, Collab, Line, Material


def get_active_brands():
    return Brand.objects.filter(products__available_flag=True).distinct().order_by("name")


def get_active_categories():
    return (
        Category.objects
        .filter(products__available_flag=True)
        .distinct()
        .select_related("parent")
    )


def get_active_lines():
    return (
        Line.objects
        .filter(products__available_flag=True)
        .distinct()
        .select_related("parent_line")
        .prefetch_related("children_line")
    )


def get_active_collabs():
    return Collab.objects.filter(products__available_flag=True).distinct().order_by("name")


def get_active_materials():
    return Material.objects.filter(products__available_flag=True).distinct().order_by("name")
