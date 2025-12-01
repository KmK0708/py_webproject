# 🚀 다음 단계 및 할 일 목록

**작성일:** 2025-11-06
**프로젝트 완성도:** 약 75%

---

## 📊 현재 프로젝트 분석

### ✅ 완성된 주요 기능

#### 1. **Backend API (Flask)**
- ✅ Binance API 연동 (모든 USDT 페어 코인 지원)
- ✅ 페이지네이션 API (`/api/current-prices?page=1&limit=20`)
- ✅ 공포&탐욕 지수 API (`/api/fear-greed`)
- ✅ 데이터 저장 API (`/api/save-current-data`)
- ✅ SQLite 데이터베이스 연동
- ✅ CORS 설정 완료

#### 2. **Frontend (React)**
- ✅ Chart.js 차트 라이브러리 설치됨
- ✅ 공포&탐욕 차트 컴포넌트 (FearGreedChart)
- ✅ 공포&탐욕 게이지 컴포넌트 (FearGreedGauge)
- ✅ React Paginate 페이지네이션
- ✅ Bootstrap UI 프레임워크
- ✅ 다크 테마 디자인
- ✅ 자동/수동 새로고침

#### 3. **설치된 라이브러리**
```json
{
  "chart.js": "^4.5.1",           // ✅ 차트 라이브러리
  "react-chartjs-2": "^5.3.1",    // ✅ React용 Chart.js
  "react-d3-speedometer": "^3.1.1", // ✅ 게이지 차트
  "react-paginate": "^8.3.0",     // ✅ 페이지네이션
  "bootstrap": "^5.3.8"           // ✅ UI 프레임워크
}
```

---

## 🎯 코드 구조 분석

### Frontend 컴포넌트

#### **FearGreedChart.jsx** (완성도: 100%)
```jsx
// Chart.js 사용
import { Line } from 'react-chartjs-2'

// 특징:
// - 최근 30일 공포&탐욕 지수 라인 차트
// - 색상 코딩 (빨강/주황/노랑/초록)
// - 다크 테마 스타일
```

#### **FearGreedGauge.jsx** (완성도: 100%)
```jsx
// react-d3-speedometer 사용
import ReactSpeedometer from 'react-d3-speedometer'

// 특징:
// - 현재 공포&탐욕 지수 게이지
// - 5단계 색상 구분
// - 0-100 값 표시
```

#### **Posts.jsx** (완성도: 5%)
```jsx
// 현재: 빈 컴포넌트
function Posts() {
  return <div>Posts</div>
}

// 예상 목적: 뉴스/포스트 표시
```

#### **App.js** (완성도: 90%)
```jsx
// 구현된 기능:
// ✅ 페이지네이션 (react-paginate)
// ✅ 공포&탐욕 차트/게이지 통합
// ✅ 코인 목록 표시
// ✅ 자동 새로고침

// 누락된 기능:
// ❌ 가격 추이 차트 (히스토리 데이터 차트)
// ❌ 거래량 차트
```

### Backend API

#### **binance_api.py** (완성도: 100%)
```python
# 주요 메서드:
# ✅ get_all_symbols() - 모든 USDT 페어 조회
# ✅ get_current_price() - 단일 코인 가격
# ✅ get_24h_ticker() - 24시간 데이터
# ✅ get_multiple_tickers() - 여러 코인 조회
```

#### **app.py** (완성도: 90%)
```python
# API 엔드포인트:
# ✅ /api/health
# ✅ /api/current-prices (페이지네이션)
# ✅ /api/history/<symbol>
# ✅ /api/save-current-data
# ✅ /api/stats
# ✅ /api/fear-greed

# 누락:
# ❌ 뉴스 크롤링 API
# ❌ 자동 데이터 수집 (APScheduler)
```

---

## 🎯 우선순위별 할 일

### 🔴 Priority 1: 가격 차트 추가 (즉시 가능!)

**이유:** Chart.js가 이미 설치되어 있고, FearGreedChart 참고 가능

**작업 내용:**
1. **PriceChart.jsx 컴포넌트 생성**
   ```jsx
   // FearGreedChart.jsx와 유사한 구조
   import { Line } from 'react-chartjs-2'

   function PriceChart({ symbol, historyData }) {
     // DB에 저장된 히스토리 데이터로 차트 그리기
   }
   ```

2. **VolumeChart.jsx 컴포넌트 생성**
   ```jsx
   import { Bar } from 'react-chartjs-2'

   function VolumeChart({ coins }) {
     // 여러 코인의 거래량 비교 막대 차트
   }
   ```

3. **App.js에 통합**
   ```jsx
   import PriceChart from './Components/PriceChart'
   import VolumeChart from './Components/VolumeChart'

   // 히스토리 데이터 가져오기
   const loadHistory = (symbol) => {
     fetch(`http://localhost:5000/api/history/${symbol}`)
   }
   ```

**예상 시간:** 2-3시간

---

### 🟡 Priority 2: Posts 컴포넌트 완성

**작업 내용:**

#### Backend: 뉴스 크롤링 API
```python
# backend/app.py에 추가
@app.route('/api/news')
def get_crypto_news():
    # BeautifulSoup으로 뉴스 사이트 크롤링
    # 또는 CoinDesk API 사용
    pass
```

#### Frontend: Posts.jsx 완성
```jsx
function Posts() {
  const [news, setNews] = useState([])

  useEffect(() => {
    fetch('http://localhost:5000/api/news')
      .then(res => res.json())
      .then(data => setNews(data))
  }, [])

  return (
    <div className="news-container">
      {news.map(article => (
        <NewsCard key={article.id} article={article} />
      ))}
    </div>
  )
}
```

**예상 시간:** 4-5시간

---

### 🟢 Priority 3: 자동 데이터 수집

**작업 내용:**

1. **APScheduler 설치**
   ```bash
   pip install apscheduler
   ```

2. **Backend에 스케줄러 추가**
   ```python
   from apscheduler.schedulers.background import BackgroundScheduler

   def auto_collect_data():
       coins = collector.get_multiple_tickers(COIN_SYMBOLS)
       for coin in coins:
           db.add_coin_price(coin)

   scheduler = BackgroundScheduler()
   scheduler.add_job(auto_collect_data, 'interval', minutes=5)
   scheduler.start()
   ```

**예상 시간:** 1-2시간

---

### 🔵 Priority 4: UI/UX 개선

**작업 내용:**

1. **검색 기능**
   ```jsx
   const [searchTerm, setSearchTerm] = useState('')
   const filteredCoins = coins.filter(coin =>
     coin.symbol.toLowerCase().includes(searchTerm.toLowerCase())
   )
   ```

2. **즐겨찾기 기능**
   ```jsx
   const [favorites, setFavorites] = useState([])
   // localStorage에 저장
   ```

3. **다크/라이트 모드 토글**
   ```jsx
   const [theme, setTheme] = useState('dark')
   ```

4. **차트 타임프레임 선택**
   ```jsx
   const [timeframe, setTimeframe] = useState('1D') // 1H, 4H, 1D, 1W
   ```

**예상 시간:** 3-4시간

---

## 📅 추천 개발 일정

### Week 1 (현재)
- [x] Backend/Frontend 분리 완료
- [x] 공포&탐욕 지수 완료
- [x] 페이지네이션 완료
- [ ] **가격 차트 추가** ← 지금 여기!

### Week 2
- [ ] 거래량 차트
- [ ] Posts/뉴스 기능
- [ ] 검색 기능

### Week 3
- [ ] 자동 데이터 수집
- [ ] 즐겨찾기
- [ ] UI 개선

### Week 4
- [ ] 테스트 및 버그 수정
- [ ] 성능 최적화
- [ ] 문서화

---

## 🛠 즉시 시작 가능한 작업

### 1. 가격 차트 만들기 (추천!)

**Step 1: PriceChart 컴포넌트 생성**
```bash
cd frontend/src/Components
# PriceChart.jsx 파일 생성
```

**Step 2: FearGreedChart.jsx 복사해서 수정**
```jsx
// FearGreedChart.jsx 기반으로 수정
// labels: 시간 → 히스토리 데이터의 timestamp
// data: 공포지수 → 가격 데이터
```

**Step 3: App.js에 추가**
```jsx
// State 추가
const [selectedCoin, setSelectedCoin] = useState('BTCUSDT')
const [historyData, setHistoryData] = useState([])

// 히스토리 로드
const loadHistory = (symbol) => {
  fetch(`http://localhost:5000/api/history/${symbol}`)
    .then(res => res.json())
    .then(data => setHistoryData(data.data))
}

// 렌더링
<PriceChart symbol={selectedCoin} data={historyData} />
```

---

### 2. 거래량 차트 만들기

**VolumeChart.jsx 생성**
```jsx
import { Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

function VolumeChart({ coins }) {
  const chartData = {
    labels: coins.map(c => c.symbol.replace('USDT', '')),
    datasets: [{
      label: '24h Volume',
      data: coins.map(c => c.volume),
      backgroundColor: [
        'rgba(59, 130, 246, 0.8)',
        'rgba(16, 185, 129, 0.8)',
        'rgba(139, 92, 246, 0.8)',
        'rgba(251, 146, 60, 0.8)',
        'rgba(236, 72, 153, 0.8)'
      ]
    }]
  }

  return <Bar data={chartData} options={options} />
}
```

---

### 3. Posts 컴포넌트 간단 버전

**먼저 임시 데이터로 UI 만들기**
```jsx
// Posts.jsx
function Posts() {
  const dummyNews = [
    { id: 1, title: "Bitcoin Hits New High", date: "2025-11-06" },
    { id: 2, title: "Ethereum Upgrade Coming", date: "2025-11-05" }
  ]

  return (
    <div className="posts-container">
      <h2>Crypto News</h2>
      {dummyNews.map(news => (
        <div key={news.id} className="news-card">
          <h3>{news.title}</h3>
          <p>{news.date}</p>
        </div>
      ))}
    </div>
  )
}
```

**나중에 Backend API 연결**

---

## 💡 빠른 승리 (Quick Wins)

### 1. 차트 섹션 레이아웃 준비
```jsx
// App.js에 차트 영역 추가
<div className="charts-section">
  <div className="chart-row">
    <div className="chart-col">
      <h3>Price Chart</h3>
      {/* PriceChart 컴포넌트 들어갈 자리 */}
    </div>
    <div className="chart-col">
      <h3>Volume Chart</h3>
      {/* VolumeChart 컴포넌트 들어갈 자리 */}
    </div>
  </div>
</div>
```

### 2. CSS 스타일 추가
```css
/* App.css에 추가 */
.charts-section {
  margin-top: 2rem;
}

.chart-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

@media (max-width: 768px) {
  .chart-row {
    grid-template-columns: 1fr;
  }
}
```

---

## 📚 학습 자료

### Chart.js 사용법
- [Chart.js 공식 문서](https://www.chartjs.org/docs/latest/)
- [react-chartjs-2 문서](https://react-chartjs-2.js.org/)
- 참고: `frontend/src/Components/FearGreedChart.jsx` (이미 작동하는 예제!)

### 다음 학습 주제
1. Chart.js 다양한 차트 타입 (Line, Bar, Doughnut)
2. BeautifulSoup 웹 크롤링
3. APScheduler 백그라운드 작업
4. React Context API (전역 상태 관리)

---

## 🎯 최종 목표

### 완성된 대시보드 모습
```
┌─────────────────────────────────────────┐
│  🎯 Crypto Analytics    Stats          │
├─────────────────────────────────────────┤
│  [Refresh] [Save] [Auto] [Search...]   │
├─────────────────────────────────────────┤
│  📊 공포&탐욕 지수    📈 BTC 가격 차트   │
├─────────────────────────────────────────┤
│  💰 Live Prices (페이지네이션)          │
├─────────────────────────────────────────┤
│  📊 가격 차트         📊 거래량 차트    │
├─────────────────────────────────────────┤
│  📰 Crypto News                        │
└─────────────────────────────────────────┘
```

---

## ✅ 다음 단계 요약

### 즉시 시작 (오늘!)
1. **PriceChart.jsx** 생성 (2시간)
2. **VolumeChart.jsx** 생성 (1시간)
3. App.js에 통합 (1시간)

### 이번 주 내
4. Posts.jsx UI 만들기 (2시간)
5. 검색 기능 추가 (1시간)

### 다음 주
6. 뉴스 크롤링 API (4시간)
7. 자동 데이터 수집 (2시간)
8. UI 개선 (3시간)

---

**어디서부터 시작하시겠어요?** 😊

1. **가격 차트** - Chart.js 활용 (추천!)
2. **뉴스 기능** - Posts 컴포넌트 완성
3. **자동 수집** - APScheduler 설정
4. **UI 개선** - 검색, 필터 등

제가 코드 작성을 도와드릴까요?
