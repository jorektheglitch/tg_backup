import bisect


SIZES = sorted([
    (10**(3*n), prefix)
    for n, prefix in
    enumerate((
        'q', 'r', 'y', 'z', 'a', 'f', 'p', 'n', 'µ', 'm',
        '',
        'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y', 'R', 'Q'
    ), start=-10)
])


def human_readable(n: float, unit: str, *, precision: int = 2) -> str:
    idx = bisect.bisect(SIZES, (n, ''))
    idx = max(0, min(idx-1, len(SIZES)))
    divisor, prefix = SIZES[idx]
    value = round(n/divisor, precision)
    return f"{value:.{precision}f} {prefix}{unit}"
