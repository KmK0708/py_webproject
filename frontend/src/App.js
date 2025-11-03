import { useState, useEffect } from 'react';
import ReactPaginate from "react-paginate"; // 신형
import "bootstrap/dist/css/bootstrap.min.css"; 
import FearGreedChart from './Components/FearGreedChart';
import FearGreedGauge from './Components/FearGreedGauge';
import './App.css';

const COIN_NAMES = {
  'BTCUSDT': 'Bitcoin',
  'ETHUSDT': 'Ethereum',
  'BNBUSDT': 'Binance Coin',
  'XRPUSDT': 'Ripple',
  'ADAUSDT': 'Cardano'
};

function App() {
  const [coins, setCoins] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState('');
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [message, setMessage] = useState({ text: '', type: '' });
  const [fearGreedData, setFearGreedData] = useState([]);
  // Pagination 부분
  const [page, setPage] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [limit] = useState(20); // 한 페이지당 표시 개수

  // 데이터 가져오기 함수
  const loadPrices = (pageNum = 1) => {
    setLoading(true);
    fetch(`http://localhost:5000/api/current-prices?page=${pageNum}&limit=${limit}`)
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setCoins(data.data);
          setPage(data.page);
          setTotalItems(data.total);
          setLastUpdate(data.timestamp);
          setLoading(false);
        }
      })
      .catch(err => {
        console.error('API 오류:', err);
        showMessage('서버 연결 오류: ' + err.message, 'error');
        setLoading(false);
      });
  };

  // 페이지 변경
  const handlePageChange = (pageNumber) => {
    setPage(pageNumber);
    loadPrices(pageNumber);
  };

  // 데이터 저장
  const saveData = () => {
    fetch('http://localhost:5000/api/save-current-data')
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          showMessage(data.message, 'success');
        }
      })
      .catch(err => {
        showMessage('저장 오류: ' + err.message, 'error');
      });
  };

  // 메시지 표시
  const showMessage = (text, type) => {
    setMessage({ text, type });
    setTimeout(() => setMessage({ text: '', type: '' }), 5000);
  };

  // 자동 새로고침 토글
  const toggleAutoRefresh = () => {
    setAutoRefresh(!autoRefresh);
    showMessage(
      autoRefresh ? '자동 새로고침 비활성화' : '자동 새로고침 활성화 (10초마다)',
      'success'
    );
  };

  // 초기 로드
  useEffect(() => {
    loadPrices();
  }, []);

  // 자동 새로고침
  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(loadPrices, 10000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

    // 공포 탐욕지수 데이터 불러오기
  useEffect(() => {
    fetch('http://localhost:5000/api/fear-greed')
      .then(res => res.json())
      .then(json => {
        if (json.success) {
          setFearGreedData(json.data);
        } else {
          console.error('지수 데이터 로드 실패');
        }
      })
      .catch(err => {
        console.error('지수 API 오류:', err);
      });
  }, []);

  // 숫자 포맷팅
  const formatNumber = (num) => {
    return num.toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  };

  // 거래량 포맷팅
  const formatVolume = (num) => {
    if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
    if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
    if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
    return num.toFixed(2);
  };

  if (loading && coins.length === 0) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <div>데이터 로딩 중...</div>
      </div>
    );
  }

  return (
    <div className="app">
      {/* Navbar */}
      <nav className="navbar">
        <div className="navbar-content">
          <div className="logo">
            <i className="fas fa-chart-line"></i> Crypto Analytics
          </div>
          <div className="nav-stats">
            <div className="nav-stat">
              <div className="nav-stat-label">Total Coins</div>
              <div className="nav-stat-value">{coins.length}</div>
            </div>
            <div className="nav-stat">
              <div className="nav-stat-label">24h Volume</div>
              <div className="nav-stat-value">
                ${formatVolume(coins.reduce((sum, c) => sum + (c.volume * c.current_price), 0))}
              </div>
            </div>
          </div>
        </div>
      </nav>

    {/* 공탐지수 부분 */}
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        gap: '20px',
        flexWrap: 'wrap',          // 작은 화면에서 자동 줄바꿈
        marginTop: '40px',
      }}
    >
      {/* 게이지 (오늘 지수) */}
      <div style={{ flex: 1, minWidth: '300px', maxWidth: '500px' }}>
        <FearGreedGauge index={fearGreedData[0] ? fearGreedData[0].value : null} />
      </div>

      {/* 라인 차트 (30일간 지수 변화) */}
      <div style={{
        flex: 1,
        minWidth: '300px',
        maxWidth: '600px',
        background: '#1e1e2f',
        borderRadius: '12px',
        padding: '20px'
      }}>
        <FearGreedChart data={fearGreedData} />
      </div>
    </div>

      {/* Container */}
      <div className="container">
        {/* Controls */}
        <div className="controls">
          <div className="btn-group">
            <button className="btn" onClick={loadPrices}>
              <i className="fas fa-sync-alt"></i> Refresh
            </button>
            <button className="btn btn-success" onClick={saveData}>
              <i className="fas fa-save"></i> Save Data
            </button>
            <button className="btn btn-secondary" onClick={toggleAutoRefresh}>
              <i className="fas fa-clock"></i> Auto Refresh: {autoRefresh ? 'ON' : 'OFF'}
            </button>
          </div>
          <div className="last-update">
            <i className="fas fa-clock"></i>
            <span>Last updated: {lastUpdate || '-'}</span>
          </div>
        </div>

        {/* Message Toast */}
        {message.text && (
          <div className={`message ${message.type}`}>
            {message.text}
          </div>
        )}

        {/* Market Overview */}
        <div className="market-overview">
          {coins.map(coin => (
            <div key={coin.symbol} className="overview-card">
              <div className="overview-title">{COIN_NAMES[coin.symbol] || coin.symbol.replace('USDT','')}</div>
              <div className="overview-value">${formatNumber(coin.current_price)}</div>
              <div className={`overview-change ${coin.price_change_percent >= 0 ? 'positive' : 'negative'}`}>
                <i className={`fas fa-arrow-${coin.price_change_percent >= 0 ? 'up' : 'down'}`}></i>
                {Math.abs(coin.price_change_percent).toFixed(2)}%
              </div>
            </div>
          ))}
        </div>

        {/* Coin Table */}
        <div className="coin-table">
          <div className="table-header">
            <h2 className="table-title">
              <i className="fas fa-coins"></i> Live Prices
            </h2>
          </div>
          <div className="coin-list">
            {coins.map(coin => {
              const symbol = coin.symbol.replace('USDT', '');
              const changeClass = coin.price_change_percent >= 0 ? 'positive' : 'negative';
              const changeSign = coin.price_change_percent >= 0 ? '+' : '';

              return (
                <div key={coin.symbol} className="coin-item">
                  <div className="coin-info">
                    <div className="coin-icon">{symbol.substring(0, 2)}</div>
                    <div className="coin-name">
                      <div className="coin-symbol">{symbol}</div>
                      <div className="coin-fullname">{COIN_NAMES[coin.symbol] || coin.symbol.replace('USDT','')}</div>
                    </div>
                  </div>
                  <div className="coin-price">${formatNumber(coin.current_price)}</div>
                  <div className={`coin-change ${changeClass}`}>
                    {changeSign}{coin.price_change_percent.toFixed(2)}%
                  </div>
                  <div className="coin-volume">
                    Vol: {formatVolume(coin.volume)}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
        {/* ✅ 페이지네이션 추가 */}
        <div className="pagination-container">
          <ReactPaginate
            previousLabel={"<"}
            nextLabel={">"}
            breakLabel={"..."}
            pageCount={Math.ceil(totalItems / limit)}
            marginPagesDisplayed={2}
            pageRangeDisplayed={5}
            onPageChange={(e) => handlePageChange(e.selected + 1)}
            containerClassName={"pagination"}
            activeClassName={"active"}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
