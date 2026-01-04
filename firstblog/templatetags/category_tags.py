from django import template
from firstblog.models import Category

register = template.Library()

@register.inclusion_tag('main/partials/category_tree.html')
def render_category_tree(categories):
    """
    Renders a hierarchical category tree.
    """
    # We need to pass the top-level categories to the template.
    top_level_categories = categories.filter(category_type='SUPER')
    return {'categories': top_level_categories}
