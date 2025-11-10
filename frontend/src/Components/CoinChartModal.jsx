import React, { useEffect, useRef, useState } from 'react';
import { createChart } from 'lightweight-charts';
import '../styles/CoinChartModal.css';

// 차트 데이터 캐시
const chartDataCache = {};

const CoinChartModal = ({ symbol, onClose, autoRefresh }) => {
  const chartContainerRef = useRef(null);
  const chartRef = useRef(null);
  const seriesRef = useRef(null);        // 🔸 새로 추가 (캔들 시리즈 참조)
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [interval, setInterval] = useState('1h');
  const [coinData, setCoinData] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const abortControllerRef = useRef(null);

  useEffect(() => {
    if (!symbol) return;

    // 🔸 renderChart 함수 수정 (차트 객체는 한 번만 생성)
    const renderChart = (klineData) => {
      if (!chartContainerRef.current) return;

      // 차트가 아직 생성되지 않았다면 새로 생성
      if (!chartRef.current) {
        chartRef.current = createChart(chartContainerRef.current, {
          width: chartContainerRef.current.clientWidth,
          height: 400,
          layout: {
            backgroundColor: '#1e1e2f',
            textColor: '#d1d4dc',
          },
          grid: {
            vertLines: { color: '#2b2b43' },
            horzLines: { color: '#2b2b43' },
          },
          crosshair: { mode: 1 },
          rightPriceScale: { borderColor: '#2b2b43' },
          timeScale: { borderColor: '#2b2b43', timeVisible: true, secondsVisible: false },
        });

        // 🔸 최초 1회만 시리즈 추가
        seriesRef.current = chartRef.current.addCandlestickSeries({
          upColor: '#10b981',
          downColor: '#ef4444',
          borderVisible: false,
          wickUpColor: '#10b981',
          wickDownColor: '#ef4444',
        });
      }

      // 🔸 데이터 갱신만 수행
      const formattedData = klineData.map(c => ({
        time: c.time / 1000,
        open: c.open,
        high: c.high,
        low: c.low,
        close: c.close,
      }));

      if (seriesRef.current) {
        seriesRef.current.setData(formattedData);
      }

      chartRef.current.timeScale().fitContent();
    };

    // --------------------------
    // 차트 데이터 로드
    // --------------------------
    const loadChartData = async () => {
      if (!autoRefresh) setLoading(true);  // 🔸 자동갱신 중엔 로딩 스피너 생략
      setError(null);

      if (abortControllerRef.current) abortControllerRef.current.abort();
      abortControllerRef.current = new AbortController();

      try {
        const cacheKey = `${symbol}_${interval}`;
        const now = Date.now();

        // 클라이언트 캐시 확인
        if (chartDataCache[cacheKey] && (now - chartDataCache[cacheKey].timestamp) < 30000) {
          console.log('✅ 클라이언트 캐시 사용:', cacheKey);
          const cachedData = chartDataCache[cacheKey];
          renderChart(cachedData.chartData);
          setCoinData(cachedData.coinData);
          setLoading(false);
          return;
        }

        // 서버에서 캔들 데이터 요청
        const res = await fetch(
          `http://localhost:5000/api/klines/${symbol}?interval=${interval}&limit=24`,
          { signal: abortControllerRef.current.signal }
        );
        const data = await res.json();

        if (!data.success) throw new Error(data.error || 'Failed to load chart data');

        // 현재 코인 가격 정보도 요청
        const priceRes = await fetch(`http://localhost:5000/api/current-prices?page=1&limit=1000`);
        const priceData = await priceRes.json();
        const coin = priceData.data.find(c => c.symbol === symbol);
        setCoinData(coin);

        // 클라이언트 캐시에 저장
        chartDataCache[cacheKey] = {
          chartData: data.data,
          coinData: coin,
          timestamp: now
        };

        // 🔸 차트에 데이터 세팅
        renderChart(data.data);
        setLoading(false);
      } catch (err) {
        if (err.name === 'AbortError') return;
        setError(err.message);
        setLoading(false);
      }
    };

    loadChartData();

    // cleanup (모달 닫을 때만 제거)
    return () => {
      if (abortControllerRef.current) abortControllerRef.current.abort();
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
        seriesRef.current = null;
      }
    };
  }, [symbol, interval, refreshTrigger]);

  // 자동 업데이트
  useEffect(() => {
    if (!autoRefresh || !symbol) return;
    const intervalId = setInterval(() => {
      console.log('🔄 차트 자동 업데이트:', symbol);
      const cacheKey = `${symbol}_${interval}`;
      delete chartDataCache[cacheKey];
      setRefreshTrigger(prev => prev + 1);
    }, 10000);
    return () => clearInterval(intervalId);
  }, [autoRefresh, symbol, interval]);

  // ESC로 닫기
  useEffect(() => {
    const handleEsc = (e) => e.key === 'Escape' && onClose();
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [onClose]);

  // --------------------------
  // 렌더링
  // --------------------------
  if (!symbol) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title">
            <h2>{symbol.replace('USDT', '')} / USDT</h2>
            {coinData && (
              <div className="modal-price-info">
                <span className="current-price">
                  ${coinData.current_price.toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 6,
                  })}
                </span>
                <span className={`price-change ${coinData.price_change_percent >= 0 ? 'positive' : 'negative'}`}>
                  {coinData.price_change_percent >= 0 ? '+' : ''}
                  {coinData.price_change_percent.toFixed(2)}%
                </span>
              </div>
            )}
          </div>
          <button className="close-button" onClick={onClose}>
            <i className="fas fa-times"></i>
          </button>
        </div>

        <div className="interval-selector">
          {['15m', '1h', '4h', '1d'].map((int) => (
            <button
              key={int}
              className={`interval-btn ${interval === int ? 'active' : ''}`}
              onClick={() => setInterval(int)}
            >
              {int}
            </button>
          ))}
        </div>

        <div className="chart-container">
          {loading && (
            <div className="chart-loading">
              <div className="spinner"></div>
              <p>차트 로딩 중...</p>
            </div>
          )}
          {error && (
            <div className="chart-error">
              <i className="fas fa-exclamation-triangle"></i>
              <p>차트를 불러올 수 없습니다: {error}</p>
            </div>
          )}
          <div ref={chartContainerRef} style={{ width: '100%', height: '400px' }} />
        </div>
      </div>
    </div>
  );
};

export default CoinChartModal;
