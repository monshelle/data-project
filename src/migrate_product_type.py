"""
ProductType 테이블 재구성: 일반화/특수화 계층 구조 적용
  parentId 자기참조 컬럼 추가 → 계층 탐색 가능

구조 (leaf row → Level1 중간 노드 → root 노드):
  신라면     → 라면(leaf)       → 면류   → 식품
  코카콜라   → 탄산음료(leaf)   → 음료   → 식품
  베이킹소다 → 제과제빵재료(leaf) → 식품재료 → 식품   ← 복수 타입
             → 세제/클리너(leaf)  → 청소용품 → 주방용품

leaf row: productBarcode 있음, parentId → Level1 노드 id
Level1  : productBarcode=NULL, parentId → root id
root    : productBarcode=NULL, parentId=NULL
"""

import sqlite3
from db_config import DB_PATH

db = sqlite3.connect(DB_PATH)
cur = db.cursor()

# ── 1. parentId 컬럼 추가 ─────────────────────────────────────
try:
    cur.execute("ALTER TABLE ProductType ADD COLUMN parentId INTEGER REFERENCES ProductType(id)")
    print("parentId 컬럼 추가 완료")
except Exception as e:
    if "duplicate column" in str(e).lower():
        print("parentId 컬럼 이미 존재 — SKIP")
    else:
        raise

# ── 2. 기존 데이터 초기화 ─────────────────────────────────────
cur.execute("DELETE FROM ProductType")
cur.execute("UPDATE sqlite_sequence SET seq=0 WHERE name='ProductType'")

# ── 3. 계층 노드 삽입 (productBarcode=NULL) ───────────────────
#   id 명시: leaf row의 parentId가 정확히 가리킬 수 있도록
hierarchy_nodes = [
    # id,  name,          description,             productBarcode, parentId
    # Root
    (1,  '식품',       '식음료 대분류',           None, None),
    (2,  '주방용품',   '주방·청소용품 대분류',    None, None),
    # Level 1 (식품 하위)
    (3,  '면류',       '국수·라면 등 면 제품',    None, 1),
    (4,  '과자류',     '과자·스낵류',             None, 1),
    (5,  '음료',       '음료류',                  None, 1),
    (6,  '유제품',     '우유·유가공품',           None, 1),
    (7,  '식품재료',   '요리·제과 재료',          None, 1),
    (8,  '가공식품',   '즉석·간편식품',           None, 1),
    (9,  '소스/양념',  '소스·카레·양념류',        None, 1),
    (10, '콩제품',     '두부·콩류 가공품',        None, 1),
    (11, '곡물가공',   '시리얼·곡물 가공품',      None, 1),
    (12, '빙과류',     '아이스크림·빙과',         None, 1),
    # Level 1 (주방용품 하위)
    (13, '청소용품',   '청소·세제·탈취제',        None, 2),
]
cur.executemany(
    "INSERT INTO ProductType(id, name, description, productBarcode, parentId) VALUES (?,?,?,?,?)",
    hierarchy_nodes
)

# ── 4. Leaf row 삽입 ──────────────────────────────────────────
#   (name=leaf타입명, parentId=Level1_id, productBarcode=바코드)
#   → 계층: leaf타입 → Level1 → root
#   복수 타입 제품(베이킹소다)은 서로 다른 leaf 행 2개 등록
leaf_rows = [
    # name,              parentId, productBarcode

    # 라면 ← 면류(3)
    ('라면',         3, '880200000001'),  # 신라면
    ('라면',         3, '880200000002'),  # 신라면 5입
    ('라면',         3, '880200000003'),  # 신라면 블랙
    ('라면',         3, '880300000001'),  # 진라면 매운맛
    ('라면',         3, '880300000002'),  # 진라면 순한맛
    ('라면',         3, '880300000003'),  # 진라면 매운맛 5입
    ('라면',         3, '880700000004'),  # 풀무원 생라면
    ('라면',         3, '880700000005'),  # 풀무원 정통메밀면

    # 스낵 ← 과자류(4)
    ('스낵',         4, '880200000004'),  # 새우깡
    ('스낵',         4, '880200000005'),  # 매운새우깡
    ('스낵',         4, '881000000003'),  # 포카칩 오리지널
    ('스낵',         4, '881000000004'),  # 포카칩 양파맛

    # 초콜릿과자 ← 과자류(4)
    ('초콜릿과자',   4, '880400000001'),  # 빼빼로 오리지널
    ('초콜릿과자',   4, '880400000002'),  # 아몬드 빼빼로
    ('초콜릿과자',   4, '880400000003'),  # 누드 빼빼로
    ('초콜릿과자',   4, '880400000004'),  # 칸쵸 초코
    ('초콜릿과자',   4, '880400000005'),  # 칸쵸 딸기
    ('초콜릿과자',   4, '881000000001'),  # 초코파이
    ('초콜릿과자',   4, '881000000002'),  # 초코파이 바나나맛

    # 탄산음료 ← 음료(5)
    ('탄산음료',     5, '880500000001'),  # 코카콜라 250ml
    ('탄산음료',     5, '880500000002'),  # 코카콜라 500ml
    ('탄산음료',     5, '880500000003'),  # 코카콜라 1.5L
    ('탄산음료',     5, '880500000004'),  # 스프라이트 250ml
    ('탄산음료',     5, '880500000005'),  # 스프라이트 500ml
    ('탄산음료',     5, '880500000006'),  # 스프라이트 1.5L

    # 커피 ← 음료(5)
    ('커피',         5, '880800000001'),  # 맥심 커피믹스 20입
    ('커피',         5, '880800000002'),  # 맥심 화이트골드 20입

    # 우유 ← 유제품(6)
    ('우유',         6, '880600000001'),  # 서울우유 흰우유 1L

    # 가공우유 ← 유제품(6)
    ('가공우유',     6, '880600000002'),  # 서울우유 초코우유 200ml
    ('가공우유',     6, '880600000003'),  # 서울우유 딸기우유 200ml
    ('가공우유',     6, '880900000001'),  # 바나나맛우유 240ml
    ('가공우유',     6, '880900000002'),  # 딸기맛우유 240ml

    # 제과제빵재료 ← 식품재료(7)
    ('제과제빵재료', 7, '880100000001'),  # 백설 설탕 1kg
    ('제과제빵재료', 7, '880100000002'),  # 백설 밀가루 1kg
    ('제과제빵재료', 7, '880100000003'),  # 백설 부침가루
    ('제과제빵재료', 7, '881100000001'),  # 베이킹소다 500g ← 식품 계열

    # 즉석밥 ← 가공식품(8)
    ('즉석밥',       8, '880100000004'),  # 햇반 210g
    ('즉석밥',       8, '880100000005'),  # 햇반 흑미밥

    # 카레 ← 소스/양념(9)
    ('카레',         9, '880300000004'),  # 오뚜기카레 순한맛
    ('카레',         9, '880300000005'),  # 오뚜기카레 매운맛

    # 두부 ← 콩제품(10)
    ('두부',        10, '880700000001'),  # 풀무원 순두부
    ('두부',        10, '880700000002'),  # 풀무원 연두부
    ('두부',        10, '880700000003'),  # 풀무원 두부 한모

    # 시리얼 ← 곡물가공(11)
    ('시리얼',      11, '880800000003'),  # 포스트 콘푸로스트
    ('시리얼',      11, '880800000004'),  # 포스트 오레오 오즈

    # 아이스크림 ← 빙과류(12)
    ('아이스크림',  12, '880900000003'),  # 메로나
    ('아이스크림',  12, '880900000004'),  # 투게더

    # 세제/클리너 ← 청소용품(13)
    ('세제/클리너', 13, '881100000001'),  # 베이킹소다 500g ← 주방용품 계열 (복수 타입!)
]
cur.executemany(
    "INSERT INTO ProductType(name, parentId, productBarcode) VALUES (?,?,?)",
    leaf_rows
)

db.commit()

# ── 5. 검증: 계층 탐색 ───────────────────────────────────────
def get_chains(barcode):
    """barcode에 연결된 leaf row에서 root까지 체인을 반환"""
    cur.execute(
        "SELECT id, name FROM ProductType WHERE productBarcode = ?", (barcode,)
    )
    chains = []
    for leaf_id, leaf_name in cur.fetchall():
        chain = [leaf_name]
        cur.execute("SELECT parentId FROM ProductType WHERE id = ?", (leaf_id,))
        row = cur.fetchone()
        pid = row[0] if row else None
        while pid:
            cur.execute("SELECT name, parentId FROM ProductType WHERE id = ?", (pid,))
            r = cur.fetchone()
            if r:
                chain.append(r[0])
                pid = r[1]
            else:
                break
        chains.append(' → '.join(chain))
    return chains

print("\n── 계층 탐색 검증 ──")
tests = [
    ('코카콜라 250ml',  '880500000001'),
    ('신라면',          '880200000001'),
    ('오뚜기카레 순한맛','880300000004'),
    ('베이킹소다 500g', '881100000001'),
]
for name, bc in tests:
    for chain in get_chains(bc):
        print(f"  {name:18s}: {chain}")

cur.execute("SELECT COUNT(*) FROM ProductType WHERE productBarcode IS NOT NULL")
leaf_cnt = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM ProductType WHERE productBarcode IS NULL")
node_cnt = cur.fetchone()[0]
print(f"\n계층 노드: {node_cnt}개 / leaf 행: {leaf_cnt}개")
db.close()
print("ProductType 계층 구조 재구성 완료")
