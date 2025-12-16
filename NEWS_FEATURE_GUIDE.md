# 뉴스 크롤링 기능 구현 완료 가이드

## 구현된 기능

### 1. **뉴스 크롤러** (Backend)
- **파일**: `backend/collectors/news_scraper.py`
- **기능**:
  - CoinDesk, CryptoNews, CoinTelegraph에서 뉴스 크롤링
  - 뉴스 제목에서 자동으로 관련 코인 추출 (BTC, ETH, BNB 등)
  - 중복 뉴스 제거 (URL 기반)
  - 시간 순 정렬

### 2. **데이터베이스 업데이트** (Backend)
- **파일**: `backend/database/models.py`
- **변경사항**:
  - News 테이블에 `related_coins` 필드 추가
  - URL에 unique 인덱스 추가 (중복 방지)
  - `get_news_by_coin()` 메서드 추가 (코인별 뉴스 조회)

### 3. **뉴스 API 엔드포인트** (Backend)
- **파일**: `backend/app.py`
- **새로운 엔드포인트**:
  - `GET /api/news` - 최근 뉴스 조회
    - Query: `limit`, `source`
  - `GET /api/news/<coin_symbol>` - 특정 코인 관련 뉴스
    - Query: `limit`
  - `GET /api/scrape-news` - 수동 뉴스 수집
    - Query: `limit`

### 4. **자동 뉴스 수집** (Backend - APScheduler)
- **기능**:
  - 30분마다 자동으로 뉴스 크롤링 및 저장
  - 10분마다 코인 가격 자동 저장
  - 백그라운드에서 실행되어 서버 성능에 영향 없음

### 5. **뉴스 섹션 UI** (Frontend)
- **파일**: `frontend/src/Components/NewsSection.jsx`
- **기능**:
  - 뉴스 목록 표시 (카드 형식)
  - 소스별 필터링 (CoinDesk, CryptoNews, CoinTelegraph)
  - 개수 선택 (10, 20, 50개)
  - 새로고침 버튼
  - 수동 뉴스 수집 버튼
  - 관련 코인 뱃지 표시
  - 상대 시간 표시 (5분 전, 2시간 전 등)

---

## 설치 및 실행 방법

### 1. Backend 설정

```bash
cd backend

# 새로운 패키지 설치
pip install beautifulsoup4 lxml apscheduler

# 또는 requirements.txt로 일괄 설치
pip install -r requirements.txt

# 서버 실행
python app.py
```

### 2. Frontend는 변경 없음

Frontend는 이미 실행 중이라면 자동으로 NewsSection이 표시됩니다.

---

## 사용 방법

### 1. 서버 시작 후 초기 뉴스 수집

서버를 처음 시작하면 뉴스가 없으므로:

1. 브라우저에서 `http://localhost:3000` 접속
2. 하단의 "📰 Crypto News" 섹션으로 스크롤
3. **"뉴스 수집"** 버튼 클릭
4. 약 10-20초 후 30개의 뉴스가 수집됨

### 2. 뉴스 필터링

- **소스별 필터**: 드롭다운에서 CoinDesk, CryptoNews 등 선택
- **개수 선택**: 10개, 20개, 50개 중 선택
- **새로고침**: 새로운 뉴스가 있는지 확인

### 3. 자동 수집 (백그라운드)

서버가 실행 중이면:
- **30분마다** 자동으로 새로운 뉴스 수집
- **10분마다** 코인 가격 자동 저장

---

## API 테스트

### 뉴스 조회
```bash
# 최근 20개 뉴스
curl http://localhost:5000/api/news?limit=20

# CoinDesk 뉴스만
curl http://localhost:5000/api/news?source=CoinDesk

# BTC 관련 뉴스만
curl http://localhost:5000/api/news/BTC
```

### 수동 뉴스 수집
```bash
curl http://localhost:5000/api/scrape-news?limit=10
```

---

## 파일 구조

```
backend/
├── app.py                          # ✅ 수정됨 (뉴스 API + 스케줄러 추가)
├── requirements.txt                # ✅ 수정됨 (beautifulsoup4, lxml, apscheduler 추가)
├── collectors/
│   ├── binance_api.py
│   └── news_scraper.py            # ✅ 새로 생성
└── database/
    └── models.py                   # ✅ 수정됨 (News 테이블 확장)

frontend/
├── src/
│   ├── App.js                      # ✅ 수정됨 (NewsSection 추가)
│   ├── Components/
│   │   └── NewsSection.jsx        # ✅ 새로 생성
│   └── styles/
│       └── NewsSection.css         # ✅ 새로 생성
```

---

## 주요 기능 설명

### 1. 코인 언급 자동 추출

뉴스 제목에서 자동으로 코인을 추출합니다:

- "Bitcoin reaches new all-time high" → **BTC**
- "Ethereum 2.0 upgrade" → **ETH**
- "Binance launches new feature" → **BNB**

### 2. 중복 뉴스 방지

- URL을 기준으로 중복 뉴스 자동 제거
- 데이터베이스에 unique 인덱스 설정

### 3. 백그라운드 스케줄러

```python
# 뉴스: 30분마다
scheduler.add_job(auto_collect_news, trigger="interval", minutes=30)

# 가격: 10분마다
scheduler.add_job(auto_save_prices, trigger="interval", minutes=10)
```

---

## 다음 단계 (선택사항)

### 1. 감정 분석 추가

뉴스 제목의 긍정/부정 감정 분석:
```bash
pip install textblob
```

### 2. 더 많은 소스 추가

- Decrypt
- Bitcoin Magazine
- The Block

### 3. 뉴스 알림 기능

특정 코인 관련 뉴스가 나오면 알림 전송

### 4. 데이터베이스 마이그레이션

SQLite → PostgreSQL (웹 배포용)

---

## 트러블슈팅

### 문제 1: 뉴스가 수집되지 않음

**원인**: 웹사이트 구조 변경

**해결**:
```python
# news_scraper.py의 CSS 선택자 수정
articles = soup.find_all('article', limit=limit)
```

### 문제 2: 스케줄러가 2번 실행됨

**원인**: Flask debug mode의 reloader

**해결**:
```python
# app.py 마지막 줄
app.run(debug=True, use_reloader=False)  # ✅ 이미 적용됨
```

### 문제 3: CORS 에러

**원인**: CORS 설정 누락

**해결**: 이미 적용되어 있음 (`flask-cors` 사용)

---

## 요약

✅ **완료된 작업**:
1. 뉴스 크롤러 구현 (3개 소스)
2. 데이터베이스 News 테이블 확장
3. 뉴스 API 엔드포인트 3개 추가
4. 자동 뉴스 수집 (30분 간격)
5. Frontend 뉴스 섹션 UI

📊 **통계**:
- 새로운 파일: 3개
- 수정된 파일: 3개
- 새로운 API: 3개
- 새로운 Python 패키지: 3개

🎯 **결과**:
이제 프로젝트가 **완전한 암호화폐 뉴스 대시보드**가 되었습니다!

---

**작성일**: 2025-11-17
**버전**: 1.0
