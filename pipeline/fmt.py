"""How numbers are written on the site. Each stat gets four forms:

long   for prose          "$9.30 billion", "34.2 percent", "seven"
short  for charts, tables "$9.30B", "34.2%", "7"
title  for headlines      "$9.30 Billion", "34.2%", "Seven"
cap    for a sentence start: long with a capital letter
"""

WORDS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']


def _num(v, digits):
    return f'{v:,.{digits}f}'


def usd_m(v, digits=None):
    if abs(v) >= 1000:
        d = 2 if digits is None else digits
        n = _num(v / 1000, d)
        return f'${n} billion', f'${n}B', f'${n} Billion'
    d = digits if digits is not None else (0 if abs(v) >= 10 else 1)
    n = _num(v, d)
    return f'${n} million', f'${n}M', f'${n} Million'


def display(value, unit, digits=None):
    if unit == 'usd_m':
        long, short, title = usd_m(value, digits)
    elif unit == 'usd':
        n = '$' + _num(value, digits or 0)
        long = short = title = n
    elif unit == 'pct':
        n = _num(value, 1 if digits is None else digits)
        long, short, title = f'{n} percent', f'{n}%', f'{n}%'
    elif unit == 'count':
        if value != int(value):
            raise ValueError(f'count {value} is not a whole number')
        v = int(value)
        short = f'{v:,}'
        long = WORDS[v] if 0 <= v < 10 else short
        title = long[0].upper() + long[1:]
    elif unit == 'year':
        long = short = title = str(int(value))
    elif unit == 'number':
        n = _num(value, 1 if digits is None else digits)
        long = short = title = n
    else:
        raise ValueError(unit)
    return {'long': long, 'short': short, 'title': title, 'cap': long[0].upper() + long[1:]}
