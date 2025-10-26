# 코인 시세 분석 대시보드

> **Binance API + React + Flask** 실시간 암호화폐 시세 모니터링 웹 애플리케이션

## 📊 프로젝트 개요

Binance API를 활용하여 실시간 암호화폐 시세를 수집하고, React와 Flask를 이용한 Full Stack 웹 대시보드입니다.

### 주요 기능
- ✅ 실시간 코인 시세 조회 (BTC, ETH, BNB, XRP, ADA)
- ✅ 시계열 가격 차트 시각화
- ✅ 24시간 거래량 비교
- ✅ 데이터베이스 저장 및 히스토리 조회
- ✅ 반응형 웹 디자인

---

## 🛠 기술 스택

### Frontend
- **React** 18
- **CSS** (다크 테마)
- **Recharts** (향후 추가 예정)

### Backend
- **Python** 3.x
- **Flask** - REST API 서버
- **SQLAlchemy** - ORM
- **SQLite** - 데이터베이스
- **Binance API** - 실시간 시세 데이터

---

## 📁 프로젝트 구조

```
py_webproject/
│
├── backend/                    # Flask REST API 서버
│   ├── app.py                 # 메인 API 서버
│   ├── requirements.txt       # Python 의존성
│   ├── collectors/
│   │   └── binance_api.py    # Binance API 수집
│   └── database/
│       └── models.py         # SQLAlchemy 모델
│
├── frontend/                   # React 애플리케이션
│   ├── package.json           # npm 의존성
│   ├── public/
│   └── src/
│       ├── App.js            # 메인 React 컴포넌트
│       └── App.css           # 스타일
│
└── docs/                      # 문서 (선택)
    └── API.md                # API 문서
```

---

## 🚀 빠른 시작

### 필수 요구사항
- Python 3.8 이상
- Node.js 18 이상
- npm 또는 yarn

### 1. Backend 실행

```bash
# 1. backend 폴더로 이동
cd backend

# 2. 가상환경 활성화 (선택)
# Windows: pyweb\Scripts\activate
# Mac/Linux: source pyweb/bin/activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 서버 실행
python app.py
```

**실행 확인:** http://localhost:5000/api/health

### 2. Frontend 실행

**새 터미널을 열고:**

```bash
# 1. frontend 폴더로 이동
cd frontend

# 2. 의존성 설치 (최초 1회만)
npm install

# 3. 개발 서버 실행
npm start
```

**실행 확인:** http://localhost:3000 자동으로 열림

---

## 📡 API 엔드포인트

### Base URL
```
http://localhost:5000
```

### 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/health` | 서버 상태 확인 |
| GET | `/api/current-prices` | 현재 코인 시세 조회 |
| GET | `/api/history/<symbol>` | 특정 코인 히스토리 |
| GET | `/api/save-current-data` | 현재 데이터 저장 |
| GET | `/api/stats` | 통계 정보 |

### 예시

```bash
# 현재 시세 조회
curl http://localhost:5000/api/current-prices

# BTC 히스토리 조회
curl http://localhost:5000/api/history/BTCUSDT

# 데이터 저장
curl http://localhost:5000/api/save-current-data
```

---

## 🎯 주요 기능 사용법

### 1. 실시간 시세 확인
- Frontend 접속 시 자동으로 최신 시세 표시
- Refresh 버튼으로 수동 갱신
- Auto Refresh로 10초마다 자동 갱신

### 2. 데이터 수집
- "Save Data" 버튼 클릭
- 5-10분 간격으로 여러 번 클릭하여 히스토리 데이터 축적

### 3. 차트 확인
- 드롭다운에서 코인 선택
- 저장된 데이터가 차트로 표시
- 최소 2-3개 시점의 데이터 필요

---

## 🔧 개발 가이드

### Backend 개발

```python
# 새로운 API 엔드포인트 추가
@app.route('/api/new-endpoint')
def new_endpoint():
    return jsonify({'success': True, 'data': []})
```

### Frontend 개발

```jsx
// API 호출
useEffect(() => {
  fetch('http://localhost:5000/api/current-prices')
    .then(res => res.json())
    .then(data => setCoins(data.data));
}, []);
```

---

## 📚 학습 자료

### React 기초
- [React 공식 문서](https://react.dev/learn) - 최고의 자료
- [생활코딩 React](https://opentutorials.org/course/4900) - 한글
- YouTube: "노마드코더 React", "드림코딩 React"

### Flask API
- [Flask 공식 문서](https://flask.palletsprojects.com/)
- [Flask-CORS 문서](https://flask-cors.readthedocs.io/)

---

## 🐛 문제 해결

### Backend 실행 오류
```bash
# flask-cors 재설치
pip install flask-cors

# 서버 재시작
python app.py
```

### Frontend CORS 오류
- Backend가 실행 중인지 확인
- `backend/app.py`에서 `CORS(app)` 설정 확인

### npm 오류
```bash
cd frontend
rm -rf node_modules
npm install
npm start
```

---

## 📈 다음 단계 (향후 개발)

### 단기 (1-2주)
- [ ] React 컴포넌트 완성
- [ ] Recharts 차트 추가
- [ ] 반응형 UI 개선

### 중기 (3-4주)
- [ ] 자동 데이터 수집 (APScheduler)
- [ ] 뉴스 크롤링 추가
- [ ] 이동평균선 등 기술적 지표

### 장기 (5-8주)
- [ ] 사용자 인증
- [ ] 알림 기능
- [ ] 배포 (Render/Vercel)

---

## 📝 라이선스

MIT License - 자유롭게 사용 가능

---

## 👤 개발자

대학생 개인 프로젝트 (포트폴리오용)

---

## 🙏 참고 자료

- [Binance API Documentation](https://binance-docs.github.io/apidocs/)
- [CoinMarketCap](https://coinmarketcap.com/) - UI 참고
- [TradingView](https://www.tradingview.com/) - 차트 참고

---

**프로젝트 시작:** 2025-10-21
**최종 업데이트:** 2025-10-25
**상태:** 🟢 개발 진행 중
