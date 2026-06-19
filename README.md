# Emart DB Management System

이마트 판매 데이터를 기반으로 한 CLI 데이터베이스 관리 시스템입니다.  
DBA 관리, OLAP 분석, 고객·공급업체 인터페이스, 자동 발주 기능을 제공합니다.

---

## 실행 방법

### 1. 사전 요구사항

- Python 3.8 이상
- 추가 패키지 설치 불필요 (표준 라이브러리만 사용)

### 2. 데이터베이스 파일 준비

데이터베이스 파일(`emart.db`)은 저장소에 포함되지 않습니다.  
아래 링크에서 다운로드한 후 `database/` 폴더에 배치하세요.

```text
📥 다운로드 링크: [https://drive.google.com/drive/folders/1b-4PHH2ZW7wgb_KGvXZ6wALlS_OsT6mb?usp=drive_link]
```

```text
배치 위치:
project-root/
└── database/
    └── emart.db   ← 여기에 넣으세요
```

### 3. 인터페이스 실행

프로젝트 루트 디렉토리에서 아래 명령어를 실행합니다.

```bash
python main.py
```

실행하면 다음과 같은 메인 메뉴가 표시됩니다.

```text
==============================================================
  Emart DB Management System
==============================================================
  1. DBA Management
  2. OLAP
  3. Customer Interface
  4. Auto Reorder
  5. Supplier Interface
  0. Exit
```

### 4. Sample 쿼리 실행

`src/sample/` 폴더의 쿼리들은 메인 앱 없이 독립 실행이 가능합니다.  
각 스크립트는 `python -m` 없이 직접 실행할 수 있습니다.

```bash
python src/sample/q1_restock_priority.py
python src/sample/q2_customer_loyalty.py
python src/sample/q3_supplier_performance.py
python src/sample/q4_bestseller_stock_coverage.py
python src/sample/q5_monthly_category_growth.py
python src/sample/q6_shinla_vs_jin.py
```

| 파일                         | 쿼리 주제                  | 사용 기능                  |
| ---------------------------- | -------------------------- | -------------------------- |
| q1_restock_priority          | 재입고 우선순위            | CTE + 날짜 필터 + 서브쿼리 |
| q2_customer_loyalty          | 매장별 고객 충성도         | CTE + CASE + GROUP BY      |
| q3_supplier_performance      | 공급업체 납품 성과         | 다중 테이블 조인 + NULLIF  |
| q4_bestseller_stock_coverage | 베스트셀러 재고 커버리지   | ROW_NUMBER 윈도우 함수     |
| q5_monthly_category_growth   | 월별 카테고리 매출 성장률  | LAG 윈도우 함수            |
| q6_shinla_vs_jin             | 신라면 vs 진라면 매장 비교 | CTE + LEFT JOIN            |

---

## 디렉토리 구조

```text
project-root/
├── main.py                      ← 실행 진입점 (이 파일만 실행하면 됨)
├── README.md
├── .gitignore
│
├── database/                    ← DB 파일 (Git 미포함 — 별도 다운로드)
│   └── emart.db
│
├── src/                         ← 전체 소스 코드
│   │
│   ├── [인터페이스 모듈]
│   ├── main.py                  ← 메인 메뉴 (루트 main.py에서 호출)
│   ├── db_config.py             ← DB 경로 설정 (환경변수 EMART_DB_PATH 지원)
│   ├── utils.py                 ← 공통 유틸리티 (DB 연결, 출력 포맷)
│   ├── dba.py                   ← DBA 관리 메뉴
│   ├── olap.py                  ← OLAP 분석 메뉴
│   ├── customer.py              ← 고객 인터페이스
│   ├── reorder.py               ← 자동 발주 메뉴
│   ├── supplier.py              ← 공급업체 인터페이스
│   │
│   ├── [데이터 구축 스크립트 — 최초 1회 실행용]
│   ├── sample_data.py           ← 초기 샘플 데이터 삽입
│   ├── add_diverse_data.py      ← 분석용 추가 데이터 (매장·고객·판매 확장)
│   ├── add_baking_soda.py       ← 베이킹소다 제품·재고·판매 데이터 추가
│   ├── migrate_product_type.py  ← ProductType 일반화/특수화 계층 구조 구성
│   │
│   ├── sample/                  ← DB 기능 검증용 독립 실행 쿼리 모음
│   │   ├── q1_restock_priority.py          ← 재입고 우선순위 (재고 부족 상품의 일평균 판매량·잔여 일수)
│   │   ├── q2_customer_loyalty.py          ← 매장별 고객 충성도 (재방문율·1인 평균 구매액)
│   │   ├── q3_supplier_performance.py      ← 공급업체 납품 성과 (주문 완료율·납품 품목 수)
│   │   ├── q4_bestseller_stock_coverage.py ← 베스트셀러 재고 커버리지 (상위 20개 제품의 재고 일수)
│   │   ├── q5_monthly_category_growth.py   ← 월별 카테고리 매출 성장률 (LAG 윈도우 함수)
│   │   └── q6_shinla_vs_jin.py             ← 신라면이 진라면보다 많이 팔린 매장 집계
│   │
│   └── [개발·검증용 스크립트]
│       ├── all_products.py      ← 전체 상품 목록 출력
│       ├── check_brands.py      ← 브랜드 데이터 확인
│       ├── check_cola.py        ← 콜라 판매 데이터 확인
│       ├── check_current.py     ← 현재 DB 상태 확인
│       ├── check_milk.py        ← 우유 판매 데이터 확인
│       ├── check_schema.py      ← 테이블 스키마 확인
│       ├── inspect_db.py        ← 각 테이블 상위 5행 출력
│       ├── milk_basket.py       ← 우유와 함께 구매된 상품 TOP 3
│       ├── top5_stores.py       ← 매출 상위 5개 매장
│       ├── insert_milk.py       ← 우유 데이터 삽입
│       └── queries.py           ← 기타 조회 쿼리
│
└── test/                        ← 단위 테스트
    ├── test_all.py
    ├── test_new_olap.py
    ├── test_reorder.py
    ├── test_reorder_history.py
    └── test_wl.py
```

---

## 메뉴 구성

### 1. DBA Management

테이블 통계, 재고 현황, 발주 내역, 무결성 검사, ProductType 관리

### 2. OLAP Analytics

- 매장별 매출 순위(Sales Ranking By Store)
- 상품별 매출 TOP 10(Top 10 Products by Revenue)
- 지역별 판매 현황(Sales by Region)
- 월별 매출 추이(Monthly Sales Trend)
- 매장/지역별 TOP 20 상품(Top 20 Products per Store)
- 장바구니 분석 (키워드 기반 동시 구매 상품)(Basket Analysis)
- 카테고리별 매출 (ProductType 계층 기반)(Category Revenue, Category By Region, Monthly Category Trend)
- 고객 등급 분석(Customer Grade Analysis)
- 지역별 매출 Top 20(Top 20 Products by Region)

### 3. Customer Interface

회원가입·로그인, 상품 검색, 장바구니 담기·결제

### 4. Auto Reorder

재고 부족 알림, 자동 발주 생성, 발주 이력 조회

### 5. Supplier Interface

공급업체별 납품 현황 조회 및 납품 처리

---

## 데이터 모델 주요 특징

**ProductType 계층 구조** (`src/migrate_product_type.py` 참조)

제품 타입은 일반화/특수화 3단계 계층으로 표현됩니다.

```text
신라면   → 라면(leaf)       → 면류  → 식품
코카콜라 → 탄산음료(leaf)   → 음료  → 식품
베이킹소다 → 제과제빵재료(leaf) → 식품재료 → 식품   ┐ 복수 타입
           → 세제/클리너(leaf)  → 청소용품 → 주방용품 ┘
```

복수 타입 제품은 각 카테고리 집계에 모두 반영됩니다.

---

## DB 경로 커스텀 설정

기본 경로(`database/emart.db`) 대신 다른 경로를 사용하려면 환경변수를 설정합니다.

```bash
# Linux / macOS
export EMART_DB_PATH=/path/to/emart.db
python main.py

# Windows PowerShell
$env:EMART_DB_PATH = "C:\path\to\emart.db"
python main.py
```
