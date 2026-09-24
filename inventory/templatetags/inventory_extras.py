from django import template

register = template.Library()

STATUS_MAP = {
    "out": ("Out of stock", "bg-danger", "border-danger"),
    "low": ("Order recommended", "bg-warning text-dark", "border-warning"),
    "ok": ("In stock", "bg-success", "border-success"),
}


@register.simple_tag
def stock_status(part):
    if part.total <= 0:
        key = "out"
    elif part.total <= part.min_level:
        key = "low"
    else:
        key = "ok"
    label, badge, border = STATUS_MAP[key]
    return {"label": label, "badge": badge, "border": border}