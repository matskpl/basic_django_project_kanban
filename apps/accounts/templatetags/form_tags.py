from django import template

register = template.Library()


@register.filter(name="add_class")
def add_class(field, css_class):
    if field is None:
        return ""

    existing = field.field.widget.attrs.get("class", "")
    existing_classes = existing.split()
    new_classes = css_class.split()

    for cls in new_classes:
        if cls not in existing_classes:
            existing_classes.append(cls)

    return field.as_widget(attrs={"class": " ".join(existing_classes).strip()})
