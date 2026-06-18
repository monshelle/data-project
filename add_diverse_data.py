"""
다양한 분석이 가능하도록 sample data 추가
- 매장  : 서울 5 → 전국 10 (부산 2, 대구/인천/대전 각 1)
- 공급업체: 6 → 10
- 브랜드  : 11 → 19
- 제품   : 29 → 45  (두부, 커피, 시리얼, 빙과, 과자 카테고리 추가)
- 고객   : 15 → 50
- 판매   : 130 → ~630  (계절/지역/카테고리 패턴 반영)
"""

import sqlite3
import random
from datetime import datetime, timedelta, date

DB = 'c:/Dev/minji-db-work/emart.db'
random.seed(42)

db = sqlite3.connect(DB)
cur = db.cursor()

# ══════════════════════════════════════════════════════════════
# 1. 기준 데이터 (Store / Supplier / Brand / Product)
# ══════════════════════════════════════════════════════════════

cur.executemany("INSERT INTO Store VALUES (?,?,?,?,?,?,?)", [
    (6,  '이마트 해운대점', '부산광역시 해운대구 센텀중앙로 55',    '부산', '10:00', '23:00', 1),
    (7,  '이마트 서면점',   '부산광역시 부산진구 중앙대로 680',     '부산', '10:00', '22:00', 1),
    (8,  '이마트 동성로점', '대구광역시 중구 동성로 51',             '대구', '10:00', '22:00', 1),
    (9,  '이마트 연수점',   '인천광역시 연수구 컨벤시아대로 101',    '인천', '10:00', '23:00', 1),
    (10, '이마트 둔산점',   '대전광역시 서구 둔산대로 117',          '대전', '10:00', '22:00', 1),
])

cur.executemany("INSERT INTO Supplier VALUES (?,?,?)", [
    (7,  '풀무원',   '02-1234-7777'),
    (8,  '동서식품', '02-1234-8888'),
    (9,  '빙그레',   '02-1234-9999'),
    (10, '오리온',   '02-1234-0000'),
])

cur.executemany("INSERT INTO Brand VALUES (?,?,?)", [
    (12, '풀무원두부',    7),
    (13, '풀무원면',      7),
    (14, '맥심',         8),
    (15, '포스트',       8),
    (16, '바나나맛우유',  9),
    (17, '메로나',       9),
    (18, '초코파이',     10),
    (19, '포카칩',       10),
])

new_products = [
    # 두부 (풀무원두부 brandId=12)
    ('880700000001', '풀무원 순두부',          '300g',  '팩',   1800, 12),
    ('880700000002', '풀무원 연두부',          '300g',  '팩',   1600, 12),
    ('880700000003', '풀무원 두부 한모',       '400g',  '팩',   2200, 12),
    # 면류 (풀무원면 brandId=13)
    ('880700000004', '풀무원 생라면',          '4인분', '봉지', 3200, 13),
    ('880700000005', '풀무원 정통메밀면',      '2인분', '봉지', 2800, 13),
    # 커피 (맥심 brandId=14)
    ('880800000001', '맥심 커피믹스 20입',     '20개',  '박스', 4500, 14),
    ('880800000002', '맥심 화이트골드 20입',   '20개',  '박스', 5500, 14),
    # 시리얼 (포스트 brandId=15)
    ('880800000003', '포스트 콘푸로스트',      '500g',  '박스', 4200, 15),
    ('880800000004', '포스트 오레오 오즈',     '400g',  '박스', 4800, 15),
    # 유제품 (바나나맛우유 brandId=16)
    ('880900000001', '바나나맛우유 240ml',     '240ml', '팩',   1500, 16),
    ('880900000002', '딸기맛우유 240ml',       '240ml', '팩',   1500, 16),
    # 빙과 (메로나 brandId=17)
    ('880900000003', '메로나',                 '70ml',  '개',    800, 17),
    ('880900000004', '투게더',                 '900ml', '통',   5500, 17),
    # 과자 (초코파이 brandId=18)
    ('881000000001', '초코파이',               '12개',  '박스', 3800, 18),
    ('881000000002', '초코파이 바나나맛',      '12개',  '박스', 3800, 18),
    # 과자 (포카칩 brandId=19)
    ('881000000003', '포카칩 오리지널',        '66g',   '봉지', 1800, 19),
    ('881000000004', '포카칩 양파맛',          '66g',   '봉지', 1800, 19),
]
cur.executemany("INSERT INTO Product VALUES (?,?,?,?,?,?)", new_products)

# ══════════════════════════════════════════════════════════════
# 2. 고객 (id 16-50)  — 나이대 다양하게
# ══════════════════════════════════════════════════════════════

surnames = ['김','이','박','최','정','강','조','윤','임','한','오','서','신','권','황']
first_names = [
    '민준','서연','지훈','수아','동현','예진','태양','하은','준혁','지우',
    '민기','수빈','성현','나연','지호','소현','준영','혜린','민재','나영',
    '태현','소연','준서','지현','태우','민서','지영','준성','수민','동우',
    '지효','서준','나리','도현','유진',
]
age_bands = [
    (1990, 1997),   # 20대후반~30대초반: 약 15명
    (1980, 1989),   # 30대후반~40대초반: 약 10명
    (1970, 1979),   # 40대후반~50대초반: 약 7명
    (2000, 2006),   # 20대초반         :  약 3명
]
age_pool = (
    [(1990,1997)] * 15 + [(1980,1989)] * 10 + [(1970,1979)] * 7 + [(2000,2006)] * 3
)

region_addresses = {
    '서울': ['서울특별시 강남구 ','서울특별시 마포구 ','서울특별시 송파구 '],
    '부산': ['부산광역시 해운대구 ','부산광역시 부산진구 '],
    '대구': ['대구광역시 수성구 '],
    '인천': ['인천광역시 연수구 '],
    '대전': ['대전광역시 서구 '],
}
all_regions = ['서울']*15 + ['부산']*7 + ['대구']*5 + ['인천']*5 + ['대전']*3

new_customers = []
for idx in range(35):
    cid = 16 + idx
    name = random.choice(surnames) + first_names[idx]
    phone = f'010-{random.randint(1000,9999)}-{random.randint(1000,9999)}'
    y_lo, y_hi = age_pool[idx % len(age_pool)]
    yr = random.randint(y_lo, y_hi)
    bday = f'{yr}-{random.randint(1,12):02d}-{random.randint(1,28):02d}'
    region = all_regions[idx % len(all_regions)]
    addr = random.choice(region_addresses[region]) + f'{random.randint(1,999)}번지'
    email = f'user{cid}@email.com'
    new_customers.append((cid, name, phone, bday, addr, email, f'pw{cid}', 1))

cur.executemany("INSERT INTO Customer VALUES (?,?,?,?,?,?,?,?)", new_customers)

# ══════════════════════════════════════════════════════════════
# 3. Stocks
# ══════════════════════════════════════════════════════════════

cur.execute("SELECT barcode FROM Product")
all_barcodes = [r[0] for r in cur.fetchall()]
new_barcodes  = [p[0] for p in new_products]

stocks = []
# 신규 매장(6-10): 전체 제품
for sid in range(6, 11):
    for bc in all_barcodes:
        qty     = random.randint(40, 180)
        reorder = random.choice([10, 15, 20, 25, 30])
        stocks.append((sid, bc, qty, reorder))

# 기존 매장(1-5): 신규 제품만
for sid in range(1, 6):
    for bc in new_barcodes:
        qty     = random.randint(40, 150)
        reorder = random.choice([10, 15, 20])
        stocks.append((sid, bc, qty, reorder))

cur.executemany("INSERT OR IGNORE INTO Stocks VALUES (?,?,?,?)", stocks)

# ══════════════════════════════════════════════════════════════
# 4. Sales  — 계절·지역·카테고리 패턴 반영
# ══════════════════════════════════════════════════════════════

cur.execute("SELECT barcode, price FROM Product")
price_map = {r[0]: r[1] for r in cur.fetchall()}

store_region = {
    1:'서울', 2:'서울', 3:'서울', 4:'서울', 5:'서울',
    6:'부산', 7:'부산', 8:'대구', 9:'인천', 10:'대전',
}

# 제품 카테고리
cat_map = {
    '880100000001':'주식', '880100000002':'주식', '880100000003':'주식',
    '880100000004':'주식', '880100000005':'주식',
    '880200000001':'라면', '880200000002':'라면', '880200000003':'라면',
    '880200000004':'스낵', '880200000005':'스낵',
    '880300000001':'라면', '880300000002':'라면', '880300000003':'라면',
    '880300000004':'주식', '880300000005':'주식',
    '880400000001':'과자', '880400000002':'과자', '880400000003':'과자',
    '880400000004':'과자', '880400000005':'과자',
    '880500000001':'음료', '880500000002':'음료', '880500000003':'음료',
    '880500000004':'음료', '880500000005':'음료', '880500000006':'음료',
    '880600000001':'유제품','880600000002':'유제품','880600000003':'유제품',
    '880700000001':'두부',  '880700000002':'두부',  '880700000003':'두부',
    '880700000004':'라면',  '880700000005':'라면',
    '880800000001':'커피',  '880800000002':'커피',
    '880800000003':'시리얼','880800000004':'시리얼',
    '880900000001':'유제품','880900000002':'유제품',
    '880900000003':'빙과',  '880900000004':'빙과',
    '881000000001':'과자',  '881000000002':'과자',
    '881000000003':'과자',  '881000000004':'과자',
}

# 계절 가중치 (1~6월 인덱스 0~5)
seasonal = {
    '주식':   [1.2,1.2,1.1,1.0,1.0,1.0],
    '라면':   [2.2,2.0,1.5,1.1,0.7,0.5],
    '스낵':   [1.0,1.0,1.0,1.1,1.2,1.3],
    '과자':   [1.0,1.0,1.0,1.1,1.3,1.4],
    '음료':   [0.6,0.6,0.8,1.3,2.0,2.5],
    '유제품': [1.1,1.1,1.0,1.0,1.1,1.1],
    '두부':   [1.3,1.2,1.0,1.0,0.9,0.8],
    '커피':   [1.6,1.5,1.2,1.0,0.8,0.6],
    '시리얼': [1.0,1.0,1.0,1.0,1.1,1.3],
    '빙과':   [0.1,0.1,0.4,1.0,2.0,3.0],
}

# 지역 가중치
regional = {
    '서울': {'주식':1.0,'라면':1.0,'스낵':1.0,'과자':1.0,'음료':1.0,'유제품':1.0,'두부':1.0,'커피':1.2,'시리얼':1.1,'빙과':0.9},
    '부산': {'주식':0.9,'라면':0.9,'스낵':1.1,'과자':1.0,'음료':1.3,'유제품':1.1,'두부':1.6,'커피':0.9,'시리얼':0.9,'빙과':1.3},
    '대구': {'주식':1.0,'라면':1.4,'스낵':1.2,'과자':1.3,'음료':1.0,'유제품':0.9,'두부':1.0,'커피':1.0,'시리얼':0.9,'빙과':1.0},
    '인천': {'주식':1.1,'라면':1.0,'스낵':1.0,'과자':1.0,'음료':1.0,'유제품':1.3,'두부':1.1,'커피':1.0,'시리얼':1.3,'빙과':0.9},
    '대전': {'주식':1.0,'라면':1.0,'스낵':1.0,'과자':1.0,'음료':1.0,'유제품':1.0,'두부':1.0,'커피':1.6,'시리얼':1.0,'빙과':0.9},
}

# 장바구니 템플릿 (카테고리 조합)  — 40% 확률로 사용
baskets = [
    ['라면', '주식'],               # 라면+햇반
    ['음료', '음료', '과자'],       # 음료+과자
    ['유제품', '시리얼'],           # 우유+시리얼
    ['커피', '과자', '시리얼'],     # 커피+간식
    ['빙과', '음료'],               # 여름 아이스크림
    ['두부', '주식', '주식'],       # 두부 요리
    ['라면', '라면', '스낵'],       # 라면 파티
    ['유제품', '과자'],             # 간식+음료
]

def weighted_pick(barcodes, weights, n):
    """중복 없이 n개 가중 샘플링"""
    picked = []
    pool_b = list(barcodes)
    pool_w = list(weights)
    for _ in range(n):
        if not pool_b: break
        total = sum(pool_w)
        if total == 0: break
        r = random.uniform(0, total)
        cum = 0
        for i, w in enumerate(pool_w):
            cum += w
            if r <= cum:
                picked.append(pool_b[i])
                pool_b.pop(i)
                pool_w.pop(i)
                break
    return picked

def gen_basket_barcodes(basket_cats, month_idx, region):
    """템플릿 카테고리별로 제품 1개씩 선택"""
    result = []
    used = set()
    for cat in basket_cats:
        candidates = [b for b, c in cat_map.items() if c == cat and b not in used]
        if not candidates:
            continue
        ws = [seasonal.get(cat,[1]*6)[month_idx] * regional.get(region,{}).get(cat,1.0)
              for _ in candidates]
        chosen = weighted_pick(candidates, ws, 1)
        if chosen:
            result.append(chosen[0])
            used.add(chosen[0])
    return result

# 고객당 구매 빈도 변화 (VIP vs 일반 vs 저빈도)
# VIP  (id 1-10)  : 가중치 3
# 일반 (id 11-30) : 가중치 2
# 저빈도(id 31-50): 가중치 1
customer_ids = list(range(1, 51))
customer_weights = [3]*10 + [2]*20 + [1]*20

start_dt = datetime(2026, 1, 1, 9, 0, 0)
end_dt   = datetime(2026, 6, 18, 22, 59, 59)
total_secs = int((end_dt - start_dt).total_seconds())

sales_rows = []
item_rows  = []
sale_id    = 131

for _ in range(500):
    store_id  = random.choice(list(range(1, 11)))
    region    = store_region[store_id]
    customer_id = random.choices(customer_ids, weights=customer_weights)[0]

    # 랜덤 일시 (주말에 1.5배 더 많이)
    offset = random.randint(0, total_secs)
    sale_dt = start_dt + timedelta(seconds=offset)
    # 영업시간 외 → 보정
    if not (9 <= sale_dt.hour <= 22):
        sale_dt = sale_dt.replace(hour=random.randint(10, 21))
    month_idx = sale_dt.month - 1

    # 장바구니 구성
    if random.random() < 0.40:
        # 템플릿 기반
        tmpl = random.choice(baskets)
        bcs  = gen_basket_barcodes(tmpl, month_idx, region)
        # 랜덤 1-2개 추가
        extra_n = random.randint(0, 2)
        all_ws  = [seasonal.get(cat_map.get(b,'주식'),[1]*6)[month_idx]
                   * regional.get(region,{}).get(cat_map.get(b,'주식'),1.0)
                   for b in all_barcodes]
        extras  = weighted_pick(
            [b for b in all_barcodes if b not in bcs],
            [all_ws[all_barcodes.index(b)] for b in all_barcodes if b not in bcs],
            extra_n
        )
        bcs += extras
    else:
        # 완전 가중 랜덤
        ws  = [seasonal.get(cat_map.get(b,'주식'),[1]*6)[month_idx]
               * regional.get(region,{}).get(cat_map.get(b,'주식'),1.0)
               for b in all_barcodes]
        n   = random.randint(2, 5)
        bcs = weighted_pick(all_barcodes, ws, n)

    if not bcs:
        continue

    total_price = 0
    items = []
    for bc in bcs:
        qty   = random.randint(1, 4)
        price = price_map[bc]
        items.append((sale_id, bc, qty, price))
        total_price += qty * price

    sales_rows.append((sale_id,
                       sale_dt.strftime('%Y-%m-%d %H:%M:%S'),
                       total_price, customer_id, store_id))
    item_rows.extend(items)
    sale_id += 1

cur.executemany("INSERT INTO Sales VALUES (?,?,?,?,?)", sales_rows)
cur.executemany("INSERT INTO SalesItem VALUES (?,?,?,?)", item_rows)

db.commit()
db.close()

print(f"Supplier  : 4개 추가 (총 10개)")
print(f"Brand     : 8개 추가 (총 19개)")
print(f"Product   : {len(new_products)}개 추가 (총 {29+len(new_products)}개)")
print(f"Store     : 5개 추가 (총 10개, 서울/부산/대구/인천/대전)")
print(f"Customer  : 35개 추가 (총 50개)")
print(f"Stocks    : {len(stocks)}건 추가")
print(f"Sales     : {len(sales_rows)}건 추가 (총 {130+len(sales_rows)}건)")
print(f"SalesItem : {len(item_rows)}건 추가")
