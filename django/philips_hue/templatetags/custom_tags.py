from django import template

register = template.Library()


@register.filter(name='format_dict')
def format_dict(value):
    if isinstance(value, dict):
        # Customize this to format the dictionary as you wish
        return ', '.join(f"{k}: {v}" for k, v in value.items())
    return value

# For the color, if you want to display it in a more human-understandable way, you might need to convert the XY color to a more common format like HEX or RGB


@register.filter(name='xy_to_rgb')
def xy_to_rgb(value):
    if 'xy' in value:
        x, y = value['xy']['x'], value['xy']['y']
        # Add logic to convert x, y to RGB
        # This is just a placeholder logic
        r, g, b = x * 255, y * 255, (1 - x - y) * 255
        return f"RGB({r}, {g}, {b})"
    return value
