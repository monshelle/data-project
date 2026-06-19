# Sample Query 설명

`src/sample/` 폴더에는 데이터베이스의 주요 기능을 검증하기 위한 독립 실행형 쿼리 스크립트 6개가 있습니다.  
각 스크립트는 메인 앱(`main.py`) 없이 단독으로 실행할 수 있으며, 실행 시 결과를 터미널에 출력합니다.

---

## 실행 방법

프로젝트 루트에서 아래와 같이 실행합니다.

```bash
python src/sample/q1_restock_priority.py
python src/sample/q2_customer_loyalty.py
python src/sample/q3_supplier_performance.py
python src/sample/q4_bestseller_stock_coverage.py
python src/sample/q5_monthly_category_growth.py
python src/sample/q6_shinla_vs_jin.py
```

---

## 쿼리 목록

### Q1. 재입고 우선순위 분석 — `q1_restock_priority.py`

**목적:** 재고가 재주문점(reorderPoint) 이하로 떨어진 상품을 찾아, 현재 재고가 며칠을 버틸 수 있는지 계산합니다.

**사용 테이블:** `Stocks`, `Store`, `Product`, `SalesItem`, `Sales`

**핵심 SQL 기법:**

- CTE(`recent_sales`)로 최근 30일 매장별 상품 판매량을 집계
- `LEFT JOIN`으로 최근 판매 이력이 없는 상품도 포함
- `COALESCE`로 판매 기록 없는 경우 0으로 처리
- `WHERE sk.quantity <= sk.reorderPoint` 조건으로 재입고 필요 상품 필터링
- 재고 잔여 일수: `현재재고 / (30일 판매량 / 30)`

**출력 컬럼:** 순위, 매장, 상품명, 재고, 재주문점, 일평균 판매량, 남은일수

```sql
WITH recent_sales AS (
    SELECT si.productBarcode, s.storeId, SUM(si.quantity) AS qty_30d
    FROM SalesItem si
    JOIN Sales s ON si.salesId = s.id
    WHERE s.saleDate >= DATE('now', '-30 days')
    GROUP BY si.productBarcode, s.storeId
)
SELECT st.name, p.name, sk.quantity, sk.reorderPoint,
       ROUND(COALESCE(rs.qty_30d, 0) / 30.0, 2) AS daily_avg,
       CASE WHEN COALESCE(rs.qty_30d, 0) = 0 THEN 999
            ELSE ROUND(sk.quantity / (rs.qty_30d / 30.0), 1) END AS days_left
FROM Stocks sk
JOIN Store st ON sk.storeId = st.id
JOIN Product p ON sk.productBarcode = p.barcode
LEFT JOIN recent_sales rs
       ON rs.productBarcode = sk.productBarcode AND rs.storeId = sk.storeId
WHERE sk.quantity <= sk.reorderPoint
ORDER BY days_left ASC, sk.quantity ASC
```

---

### Q2. 매장별 고객 충성도 분석 — `q2_customer_loyalty.py`

**목적:** 각 매장의 전체 고객 중 재방문(2회 이상 구매) 고객 비율과 1인당 평균 구매액을 분석합니다.

**사용 테이블:** `Sales`, `SalesItem`, `Store`, `Customer`

**핵심 SQL 기법:**

- CTE(`cust_per_store`)로 고객별·매장별 방문 횟수와 총 지출액 집계
- `CASE WHEN visit_cnt >= 2`로 충성 고객 판별
- `SUM(CASE WHEN ...) / COUNT(*) * 100`으로 충성률(%) 계산
- `AVG(total_spend)`로 1인당 평균 구매액 산출

**출력 컬럼:** 매장명, 지역, 전체고객, 충성고객, 충성률, 1인평균구매

```sql
WITH cust_per_store AS (
    SELECT s.storeId, s.customerId,
           COUNT(DISTINCT s.id) AS visit_cnt,
           SUM(si.quantity * si.unitPrice) AS total_spend
    FROM Sales s
    JOIN SalesItem si ON si.salesId = s.id
    WHERE s.customerId IS NOT NULL
    GROUP BY s.storeId, s.customerId
)
SELECT st.name, st.region,
       COUNT(*) AS total_customers,
       SUM(CASE WHEN cps.visit_cnt >= 2 THEN 1 ELSE 0 END) AS loyal_customers,
       ROUND(
           SUM(CASE WHEN cps.visit_cnt >= 2 THEN 1.0 ELSE 0 END) / COUNT(*) * 100, 1
       ) AS loyalty_rate,
       ROUND(AVG(cps.total_spend), 0) AS avg_spend_per_customer
FROM cust_per_store cps
JOIN Store st ON cps.storeId = st.id
GROUP BY st.id
ORDER BY loyalty_rate DESC
```

---

### Q3. 공급업체 납품 성과 요약 — `q3_supplier_performance.py`

**목적:** 각 공급업체의 총 주문 건수, 완료 건수, 완료율, 납품 상품 종류 수, 총 납품 수량을 한눈에 파악합니다.

**사용 테이블:** `Supplier`, `OrderTable`, `OrderItem`

**핵심 SQL 기법:**

- `LEFT JOIN`으로 주문이 없는 공급업체도 결과에 포함
- `COUNT(DISTINCT CASE WHEN ot.status = 'completed' THEN ot.id END)`으로 완료 주문만 집계
- `NULLIF(..., 0)`으로 0 나누기 방지 후 완료율(%) 계산
- `COUNT(DISTINCT oi.productBarcode)`으로 납품 상품 종류 수 산출

**출력 컬럼:** 공급업체, 총주문, 완료, 완료율, 상품종류, 총납품수량

```sql
SELECT sp.name,
       COUNT(DISTINCT ot.id) AS total_orders,
       COUNT(DISTINCT CASE WHEN ot.status = 'completed' THEN ot.id END) AS done_orders,
       ROUND(
           COUNT(DISTINCT CASE WHEN ot.status = 'completed' THEN ot.id END)
           * 100.0 / NULLIF(COUNT(DISTINCT ot.id), 0), 1
       ) AS completion_rate,
       COUNT(DISTINCT oi.productBarcode) AS product_types,
       SUM(oi.quantity) AS total_qty
FROM Supplier sp
LEFT JOIN OrderTable ot ON ot.supplierId = sp.id
LEFT JOIN OrderItem  oi ON oi.orderId    = ot.id
GROUP BY sp.id
ORDER BY total_orders DESC, completion_rate DESC
```

---

### Q4. 베스트셀러 재고 커버리지 분석 — `q4_bestseller_stock_coverage.py`

**목적:** 누적 판매량 기준 상위 20개 제품의 현재 전체 재고가 최근 판매 속도 기준으로 며칠치인지 계산합니다.

**사용 테이블:** `SalesItem`, `Sales`, `Product`, `Stocks`

**핵심 SQL 기법:**

- 4개의 CTE를 단계적으로 구성
  - `total_sales`: 제품별 누적 판매량·매출
  - `top20`: `ROW_NUMBER() OVER (ORDER BY total_qty DESC)`로 순위 부여 후 상위 20개 선별
  - `recent_30d`: 최근 30일 제품별 판매량
  - `current_stock`: 전 매장 재고 합산
- 재고 커버리지 일수: `전체재고 / (30일 판매량 / 30)`

**출력 컬럼:** 순위, 상품명, 총판매, 매출, 현재재고, 일평균, 재고일수

```sql
WITH total_sales AS (
    SELECT si.productBarcode,
           SUM(si.quantity) AS total_qty,
           SUM(si.quantity * si.unitPrice) AS total_revenue
    FROM SalesItem si GROUP BY si.productBarcode
),
top20 AS (
    SELECT productBarcode, total_qty, total_revenue,
           ROW_NUMBER() OVER (ORDER BY total_qty DESC) AS rank
    FROM total_sales LIMIT 20
),
recent_30d AS (
    SELECT si.productBarcode, SUM(si.quantity) AS qty_30d
    FROM SalesItem si JOIN Sales s ON si.salesId = s.id
    WHERE s.saleDate >= DATE('now', '-30 days')
    GROUP BY si.productBarcode
),
current_stock AS (
    SELECT productBarcode, SUM(quantity) AS total_stock
    FROM Stocks GROUP BY productBarcode
)
SELECT t.rank, p.name, t.total_qty, t.total_revenue,
       COALESCE(cs.total_stock, 0) AS current_stock,
       ROUND(COALESCE(r.qty_30d, 0) / 30.0, 2) AS daily_avg,
       CASE WHEN COALESCE(r.qty_30d, 0) = 0 THEN 999
            ELSE ROUND(COALESCE(cs.total_stock, 0) / (r.qty_30d / 30.0), 1) END AS stock_days
FROM top20 t
JOIN Product p ON t.productBarcode = p.barcode
LEFT JOIN recent_30d r ON r.productBarcode = t.productBarcode
LEFT JOIN current_stock cs ON cs.productBarcode = t.productBarcode
ORDER BY t.rank
```

---

### Q5. 월별 카테고리별 매출 성장률 — `q5_monthly_category_growth.py`

**목적:** 월별·카테고리별 매출과 전월 대비 성장률(%)을 계산해 시계열 트렌드를 파악합니다.

**사용 테이블:** `SalesItem`, `Sales`, `Product`, `ProductType`

**핵심 SQL 기법:**

- `SUBSTR(saleDate, 1, 7)`으로 연-월(YYYY-MM) 추출
- `COALESCE(pt.name, 'Uncategorized')`로 카테고리 미지정 상품 처리
- `LAG(revenue) OVER (PARTITION BY category ORDER BY month)`으로 전월 매출 참조
- 성장률: `(당월 - 전월) / 전월 * 100`, 첫 달은 NULL 처리

**출력 형식:** 월별 블록으로 구분, 카테고리·매출·전월매출·성장률 출력

```sql
WITH monthly_cat AS (
    SELECT SUBSTR(s.saleDate, 1, 7) AS month,
           COALESCE(pt.name, 'Uncategorized') AS category,
           SUM(si.quantity * si.unitPrice) AS revenue
    FROM SalesItem si
    JOIN Sales s ON si.salesId = s.id
    JOIN Product p ON si.productBarcode = p.barcode
    LEFT JOIN ProductType pt ON pt.productBarcode = p.barcode
    GROUP BY month, category
),
with_prev AS (
    SELECT month, category, revenue,
           LAG(revenue) OVER (PARTITION BY category ORDER BY month) AS prev_revenue
    FROM monthly_cat
)
SELECT month, category, revenue, prev_revenue,
       CASE WHEN prev_revenue IS NULL OR prev_revenue = 0 THEN NULL
            ELSE ROUND((revenue - prev_revenue) * 100.0 / prev_revenue, 1) END AS growth_rate
FROM with_prev
ORDER BY month DESC, revenue DESC
```

---

### Q6. 신라면 vs 진라면 매장별 판매 비교 — `q6_shinla_vs_jin.py`

**목적:** 신라면 누적 판매량이 진라면보다 많은 매장을 찾아 차이(diff)가 큰 순서로 나열합니다.

**사용 테이블:** `SalesItem`, `Product`, `Sales`, `Store`

**핵심 SQL 기법:**

- 두 개의 CTE(`shin`, `jin`)로 제품명 LIKE 검색을 통해 각 브랜드 판매량을 매장별로 집계
- `Store`를 기준으로 `LEFT JOIN`하여 한쪽만 판매된 매장도 누락 없이 포함
- `COALESCE(..., 0)`으로 판매 기록 없는 경우 0으로 처리
- `WHERE shin_qty > jin_qty` 조건으로 신라면 우세 매장만 필터링

**출력 컬럼:** 순위, 매장명, 지역, 신라면 판매량, 진라면 판매량, 차이

```sql
WITH shin AS (
    SELECT s.storeId, SUM(si.quantity) AS qty
    FROM SalesItem si
    JOIN Product p ON si.productBarcode = p.barcode
    JOIN Sales s ON si.salesId = s.id
    WHERE p.name LIKE '%신라면%'
    GROUP BY s.storeId
),
jin AS (
    SELECT s.storeId, SUM(si.quantity) AS qty
    FROM SalesItem si
    JOIN Product p ON si.productBarcode = p.barcode
    JOIN Sales s ON si.salesId = s.id
    WHERE p.name LIKE '%진라면%'
    GROUP BY s.storeId
)
SELECT st.name, st.region,
       COALESCE(shin.qty, 0)                          AS shin_qty,
       COALESCE(jin.qty, 0)                           AS jin_qty,
       COALESCE(shin.qty, 0) - COALESCE(jin.qty, 0)  AS diff
FROM Store st
LEFT JOIN shin ON st.id = shin.storeId
LEFT JOIN jin  ON st.id = jin.storeId
WHERE COALESCE(shin.qty, 0) > COALESCE(jin.qty, 0)
ORDER BY diff DESC
```

---

## 공통 사항

| 항목 | 내용 |
| --- | --- |
| DB 연결 | `db_config.py`의 `DB_PATH`를 통해 `database/emart.db` 참조 |
| 출력 정렬 | `utils.py`의 `wl()` / `wr()`로 한국어 2칸 폭 처리 |
| 경로 설정 | 각 스크립트 상단에서 `sys.path`에 `src/`를 추가해 독립 실행 가능 |
| DB 커스텀 경로 | 환경변수 `EMART_DB_PATH`로 DB 위치 변경 가능 |
