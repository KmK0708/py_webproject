import { useState, useEffect, useCallback } from 'react';
import "bootstrap/dist/css/bootstrap.min.css";
import './App.css';

// 컴포넌트 불러오기
import Navbar from './Components/Navbar';
import OverviewSection from './Components/OverviewSection';
import LivePriceSection from './Components/LivePriceSection';
import FearGreedChart from './Components/FearGreedChart';
import FearGreedGauge from './Components/FearGreedGauge';
import CoinChartModal from './Components/CoinChartModal';
import NewsSection from './Components/NewsSection';

function App() {
  // -----------------------------
  // 상태 관리 (데이터)
  // -----------------------------
  const [overviewCoins, setOverviewCoins] = useState([]);
  const [tableCoins, setTableCoins] = useState([]);
  const [fearGreedData, setFearGreedData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState('');
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [page, setPage] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [limit] = useState(20);
  const [selectedCoin, setSelectedCoin] = useState(null);

  // -----------------------------
  // 데이터 로드 함수
  // -----------------------------
  const loadPrices = useCallback((pageNum = 1) => {
    setLoading(true);
    fetch(`http://localhost:5000/api/current-prices?page=${pageNum}&limit=${limit}`)
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setOverviewCoins(data.data.slice(0, 20)); // 상단 카드용
          setTableCoins(data.data);                  // 테이블용
          setPage(data.page);
          setTotalItems(data.total);
          setLastUpdate(data.timestamp);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error('API 오류:', err);
        setLoading(false);
      });
  }, [limit]);

  // -----------------------------
  //초기 데이터 로드
  // -----------------------------
  useEffect(() => {
    loadPrices();
  }, [loadPrices]);

  // -----------------------------
  // 자동 새로고침
  // -----------------------------
  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(loadPrices, 10000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, loadPrices]);

  // -----------------------------
  // 공포·탐욕 지수 데이터
  // -----------------------------
  useEffect(() => {
    fetch('http://localhost:5000/api/fear-greed')
      .then(res => res.json())
      .then(json => setFearGreedData(json.success ? json.data : []))
      .catch(err => console.error('지수 API 오류:', err));
  }, []);

  // -----------------------------
  // 로딩 중 표시
  // -----------------------------
  if (loading)
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <div>데이터 로딩 중...</div>
      </div>
    );

  // -----------------------------
  // 화면 구성
  // -----------------------------
  return (
    <div className="app">
      {/* 상단 네비게이션 */}
      <Navbar overviewCoins={overviewCoins} />

      {/* 공포·탐욕 지수 */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          gap: '20px',
          flexWrap: 'wrap',
          marginTop: '40px',
        }}
      >
        <div style={{ flex: 1, minWidth: '300px', maxWidth: '500px' }}>
          <FearGreedGauge index={fearGreedData[0]?.value || null} />
        </div>

        <div
          style={{
            flex: 1,
            minWidth: '300px',
            maxWidth: '600px',
            background: '#1e1e2f',
            borderRadius: '12px',
            padding: '20px',
          }}
        >
          <FearGreedChart data={fearGreedData} />
        </div>
      </div>

      {/* 컨트롤 버튼 */}
      <div className="container" style={{ marginTop: '30px' }}>
        <div className="controls">
          <div className="btn-group">
            <button className="btn" onClick={() => loadPrices(page)}>
              <i className="fas fa-sync-alt"></i> Refresh
            </button>
            <button 
              className={`btn ${autoRefresh ? 'btn-success' : 'btn-secondary'}`}
              onClick={() => setAutoRefresh(!autoRefresh)}
            >
              <i className="fas fa-clock"></i> Auto Refresh: {autoRefresh ? 'ON' : 'OFF'}
            </button>
          </div>
          <div className="last-update">
            <i className="fas fa-clock"></i>
            <span>Last updated: {lastUpdate || '-'}</span>
          </div>
        </div>
      </div>
      

      {/* 블록형 코인 카드 (OverviewSection) */}
      <OverviewSection
        overviewCoins={overviewCoins}
        onCoinClick={setSelectedCoin}
      />

      {/* 실시간 테이블 (LivePriceSection) */}
      <LivePriceSection
        tableCoins={tableCoins}
        loadPrices={loadPrices}
        page={page}
        totalItems={totalItems}
        limit={limit}
        lastUpdate={lastUpdate}
      />

      {/* 뉴스 섹션 */}
      <div className="container" style={{ marginTop: '30px' }}>
        <NewsSection />
      </div>

      {/* 차트 모달 */}
      {selectedCoin && (
        <CoinChartModal
          symbol={selectedCoin}
          onClose={() => setSelectedCoin(null)}
          autoRefresh={autoRefresh}
        />
      )}
    </div>
  );
}

export default App;
