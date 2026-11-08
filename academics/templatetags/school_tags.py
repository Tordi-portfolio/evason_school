from django import template

register = template.Library()


@register.filter
def ordinal(n):
    try:
        n = int(n)
    except (TypeError, ValueError):
        return n
    suffix = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"
