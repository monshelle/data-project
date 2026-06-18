import unicodedata

def _dw(s):
    return sum(2 if unicodedata.east_asian_width(c) in ('W','F') else 1 for c in str(s))

def wl(s, w):
    s = str(s)
    return s + ' ' * max(0, w - _dw(s))

def wr(s, w):
    s = str(s)
    return ' ' * max(0, w - _dw(s)) + s

tests = [
    ('이마트 강남점',        16),
    ('이마트 해운대점',      16),
    ('백설 설탕 1kg',        28),
    ('맥심 화이트골드 20입', 28),
    ('Coca-Cola 250ml',      28),
    ('서울우유협동조합',     18),
    ('풀무원 정통메밀면',    28),
]

print("wl() alignment — '|' should line up in each group:\n")
for s, w in tests:
    padded = wl(s, w)
    display_w = _dw(padded)
    print(f"  |{padded}| dw={_dw(s):>2}  chars={len(s):>2}  field={w}  result_dw={display_w}")

print("\nBefore fix (Python built-in f-string padding):")
for s, w in tests:
    padded = f"{s:<{w}}"
    print(f"  |{padded}| (f-string :<{w})")
