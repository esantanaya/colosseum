from ast import literal_eval
from collections import Sequence

from .colors import NAMED_COLOR, hsl, rgb
from .shapes import Rect
from .units import Unit, px
from .wrappers import BorderSpacing, Quotes


def units(value):
    """Parse a unit value

    Accepts:
    * An already converted instance of unit
    * An integer (interpreted as pixels)
    * A float (interpreted as pixels)
    * A string with a known unit suffix
    * A string containing an float (interpreted as pixels)
    """
    if isinstance(value, Unit):
        return value
    elif isinstance(value, (int, float)):
        return value * px
    elif isinstance(value, str):
        for suffix, unit in Unit.UNITS:
            if value.endswith(suffix):
                try:
                    return float(value[:-len(suffix)]) * unit
                except ValueError:
                    pass

        try:
            return float(value) * px
        except ValueError:
            pass

    raise ValueError('Unknown size %s' % value)


def color(value):
    """Parse a color from a value.

    Accepts:
    * rgb() instances
    * hsl() instances
    * '#RGB'
    * '#RGBA'
    * '#RRGGBB'
    * '#RRGGBBAA'
    * 'rgb(0, 0, 0)'
    * 'rgba(0, 0, 0, 0.0)'
    * 'hsl(0, 0%, 0%)'
    * 'hsla(0, 0%, 0%, 0.0)'
    * A named color
    """

    if isinstance(value, (rgb, hsl)):
        return value

    elif isinstance(value, str):
        if value[0] == '#':
            if len(value) == 4:
                return rgb(
                    r=int(value[1] + value[1], 16),
                    g=int(value[2] + value[2], 16),
                    b=int(value[3] + value[3], 16),
                )
            elif len(value) == 5:
                return rgb(
                    r=int(value[1] + value[1], 16),
                    g=int(value[2] + value[2], 16),
                    b=int(value[3] + value[3], 16),
                    a=int(value[4] + value[4], 16) / 0xff,
                )
            elif len(value) == 7:
                return rgb(
                    r=int(value[1:3], 16),
                    g=int(value[3:5], 16),
                    b=int(value[5:7], 16),
                )
            elif len(value) == 9:
                return rgb(
                    r=int(value[1:3], 16),
                    g=int(value[3:5], 16),
                    b=int(value[5:7], 16),
                    a=int(value[7:9], 16) / 0xff,
                )
        elif value.startswith('rgba'):
            try:
                values = value[5:-1].split(',')
                if len(values) == 4:
                    return rgb(int(values[0]), int(values[1]), int(values[2]), float(values[3]))
            except ValueError:
                pass
        elif value.startswith('rgb'):
            try:
                values = value[4:-1].split(',')
                if len(values) == 3:
                    return rgb(int(values[0]), int(values[1]), int(values[2]))
            except ValueError:
                pass

        elif value.startswith('hsla'):
            try:
                values = value[5:-1].split(',')
                if len(values) == 4:
                    return hsl(
                        int(values[0]),
                        int(values[1].strip().rstrip('%')) / 100.0,
                        int(values[2].strip().rstrip('%')) / 100.0,
                        float(values[3])
                    )
            except ValueError:
                pass

        elif value.startswith('hsl'):
            try:
                values = value[4:-1].split(',')
                if len(values) == 3:
                    return hsl(
                        int(values[0]),
                        int(values[1].strip().rstrip('%')) / 100.0,
                        int(values[2].strip().rstrip('%')) / 100.0,
                    )
            except ValueError:
                pass
        else:
            try:
                return NAMED_COLOR[value.lower()]
            except KeyError:
                pass

    raise ValueError('Unknown color %s' % value)


def border_spacing(value):
    """
    Parse a border spacing value.

    Accepts:
    * A sequence object different that a string.
    * An integer (interpreted as pixels).
    * A float (interpreted as pixels).
    * A string with of 1 or 2 length items separated by spaces.
    """
    if isinstance(value, Sequence) and not isinstance(value, str):
        values = value
    elif isinstance(value, (int, float)):
        values = (value, )
    else:
        values = [x.strip() for x in value.split()]

    if len(values) == 1:
        horizontal = units(values[0])
        return BorderSpacing(horizontal)
    elif len(values) == 2:
        horizontal = units(values[0])
        vertical = units(values[1])
        return BorderSpacing(horizontal, vertical)

    raise ValueError('Unknown border spacing %s' % str(value))


def rect(value):
    """Parse a given rect shape."""
    value = ' '.join(val.strip() for val in value.split())
    if (value.startswith('rect(') and value.endswith(')') and
            value.count('rect(') == 1 and value.count(')') == 1):
        value = value.replace('rect(', '')
        value = value.replace(')', '').strip()

        values = None
        if value.count(',') == 3:
            values = value.split(',')
        elif value.count(',') == 0 and value.count(' ') == 3:
            values = value.split(' ')

        if values is not None:
            values = [units(val.strip()) for val in values]
            return Rect(*values)

    raise ValueError('Unknown shape %s' % value)


def quotes(value):
    """Parse content quotes.

    Accepts:
    * A string: "'<' '>' '{' '}'"
    * A sequence: ('<', '>') or ['{', '}']
    * A list of 2 item tuples: [('<', '>'), ('{', '}')]
    """
    if isinstance(value, str):
        values = [val.strip() for val in value.split()]
    elif isinstance(value, Sequence):
        # Flatten list of tuples
        values = [repr(item) for sublist in value for item in sublist]
    else:
        raise ValueError('Unknown quote %s' % value)

    # Length must be a multiple of 2
    if len(values) > 0 and len(values) % 2 == 0:
        parsed_values = []
        for idx in range(len(values) // 2):
            start = idx * 2
            end = start + 2
            opening, closing = values[start:end]

            try:
                opening = literal_eval(opening)
                closing = literal_eval(closing)
                parsed_values.append((opening, closing))

                if len(opening) == 0 or len(closing) == 0:
                    raise ValueError('Invalid quotes %s' % value)

            except SyntaxError:
                raise ValueError('Invalid quotes %s' % value)

        return Quotes(parsed_values)

    raise ValueError('Length of quote items must be a multiple of 2!')
