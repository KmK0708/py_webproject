import React, { useEffect, useRef, useState } from 'react';
import { createChart } from 'lightweight-charts';
import '../styles/CoinChartModal.css';
import { API_URL } from '../config';

// 차트 데이터 캐시
const chartDataCache = {};

// 이동평균선 계산 함수
const calculateMA = (data, period) => {
  const result = [];
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      result.push({ time: data[i].time, value: null });
    } else {
      let sum = 0;
      for (let j = 0; j < period; j++) {
        sum += data[i - j].close;
      }
      result.push({ time: data[i].time, value: sum / period });
    }
  }
  return result.filter(item => item.value !== null);
};

const CoinChartModal = ({ symbol, onClose, autoRefresh }) => {
  const chartContainerRef = useRef(null);
  const chartRef = useRef(null);
  const seriesRef = useRef(null);
  const ma7Ref = useRef(null);
  const ma25Ref = useRef(null);
  const ma99Ref = useRef(null);
  const volumeSeriesRef = useRef(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeframe, setTimeframe] = useState('1h');
  const [coinData, setCoinData] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [showMA, setShowMA] = useState({ ma7: true, ma25: true, ma99: true });
  const abortControllerRef = useRef(null);

  useEffect(() => {
    if (!symbol) return;

    // 차트 렌더링 함수 (이평선 + 거래량 포함)
    const renderChart = (klineData) => {
      if (!chartContainerRef.current) return;

      // 차트가 아직 생성되지 않았다면 새로 생성
      if (!chartRef.current) {
        chartRef.current = createChart(chartContainerRef.current, {
          width: chartContainerRef.current.clientWidth,
          height: 500,
          layout: {
            backgroundColor: '#1e1e2f',
            textColor: '#1c1e24ff',
            attributionLogo: false,
          },
          grid: {
            vertLines: { color: '#2b2b43' },
            horzLines: { color: '#2b2b43' },
          },
          crosshair: { mode: 1 },
          //메인 가격 축(캔들용) 세팅: 아래쪽 30% 비워두기.
          rightPriceScale: {
            borderColor: '#2b2b43',
            scaleMargins: {
              top: 0.1,    // 위쪽 10% 여백
              bottom: 0.3, // 아래쪽 30%는 거래량을 위해 비워둠
            },
          },
          timeScale: { borderColor: '#2b2b43', timeVisible: true, secondsVisible: false, timezone: 'Asia/Seoul'},

        });

        // 캔들스틱 시리즈
        seriesRef.current = chartRef.current.addCandlestickSeries({
          upColor: '#10b981',
          downColor: '#ef4444',
          borderVisible: false,
          wickUpColor: '#10b981',
          wickDownColor: '#ef4444',
          priceFormat: {
            type: 'price',
            precision: 4, //  표시할 소수점 자릿수
            minMove: 0.0001, //  6자리에 맞게 최소 움직임 설정
          },
        });

        // 거래량 시리즈 (히스토그램)
        volumeSeriesRef.current = chartRef.current.addHistogramSeries({
          color: '#26a69a',
          priceFormat: {
            type: 'volume',
          },
          priceScaleId: '',
        });

        // 거래량 시리즈의 축 세팅: 위쪽 75%를 비워둡니다.
        volumeSeriesRef.current.priceScale().applyOptions({
          scaleMargins: {
            top: 0.75, // 위쪽 75%는 캔들을 위해 비워둠
            bottom: 0,
          },
        });

        // 이동평균선 시리즈
        ma7Ref.current = chartRef.current.addLineSeries({
          color: '#2962FF',
          lineWidth: 2,
          title: 'MA7',
        });

        ma25Ref.current = chartRef.current.addLineSeries({
          color: '#FF6D00',
          lineWidth: 2,
          title: 'MA25',
        });

        ma99Ref.current = chartRef.current.addLineSeries({
          color: '#9C27B0',
          lineWidth: 2,
          title: 'MA99',
        });
      }

      // 데이터 변환 (UTC를 한국 시간으로 변환: UTC+9)
      const formattedData = klineData.map(c => ({
        time: Math.floor(c.time / 1000) + (9 * 60 * 60), // UTC+9 (한국 시간)
        open: c.open,
        high: c.high,
        low: c.low,
        close: c.close,
        value: c.volume,
      }));

      // 캔들스틱 데이터 설정
      if (seriesRef.current) {
        seriesRef.current.setData(formattedData);
      }

      // 거래량 데이터 설정
      if (volumeSeriesRef.current) {
        const volumeData = formattedData.map(d => ({
          time: d.time,
          value: d.value,
          color: d.close >= d.open ? 'rgba(16, 185, 129, 0.5)' : 'rgba(239, 68, 68, 0.5)',
        }));
        volumeSeriesRef.current.setData(volumeData);
      }

      // 이동평균선 계산 및 설정
      if (showMA.ma7 && ma7Ref.current) {
        const ma7Data = calculateMA(formattedData, 7);
        ma7Ref.current.setData(ma7Data);
      }

      if (showMA.ma25 && ma25Ref.current) {
        const ma25Data = calculateMA(formattedData, 25);
        ma25Ref.current.setData(ma25Data);
      }

      if (showMA.ma99 && ma99Ref.current) {
        const ma99Data = calculateMA(formattedData, 99);
        ma99Ref.current.setData(ma99Data);
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
        const cacheKey = `${symbol}_${timeframe}`;
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
          `${API_URL}/api/klines/${symbol}?interval=${timeframe}&limit=120`,
          { signal: abortControllerRef.current.signal }
        );
        const data = await res.json();

        if (!data.success) throw new Error(data.error || 'Failed to load chart data');

        // 현재 코인 가격 정보도 요청
        const priceRes = await fetch(`${API_URL}/api/current-prices?page=1&limit=1000`);
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
        ma7Ref.current = null;
        ma25Ref.current = null;
        ma99Ref.current = null;
        volumeSeriesRef.current = null;
      }
    };
  }, [symbol, timeframe, refreshTrigger, showMA]);

  // 자동 업데이트
  useEffect(() => {
    if (!autoRefresh || !symbol) return;
    const intervalId = window.setInterval(() => {
      console.log('🔄 차트 자동 업데이트:', symbol);
      const cacheKey = `${symbol}_${timeframe}`;
      delete chartDataCache[cacheKey];
      setRefreshTrigger(prev => prev + 1);
    }, 10000);
    return () => window.clearInterval(intervalId);
  }, [autoRefresh, symbol, timeframe]);

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
                    minimumFractionDigits: 4,
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

        <div className="chart-controls">
          <div className="interval-selector">
            <label>Time:</label>
            {['15m', '1h', '4h', '1d'].map((int) => (
              <button
                key={int}
                className={`interval-btn ${timeframe === int ? 'active' : ''}`}
                onClick={() => setTimeframe(int)}
              >
                {int}
              </button>
            ))}
          </div>

          <div className="ma-selector">
            <label>MA:</label>
            <button
              className={`ma-btn ${showMA.ma7 ? 'active' : ''}`}
              onClick={() => setShowMA(prev => ({ ...prev, ma7: !prev.ma7 }))}
              style={{ color: showMA.ma7 ? '#2962FF' : '#94a3b8' }}
            >
              7
            </button>
            <button
              className={`ma-btn ${showMA.ma25 ? 'active' : ''}`}
              onClick={() => setShowMA(prev => ({ ...prev, ma25: !prev.ma25 }))}
              style={{ color: showMA.ma25 ? '#FF6D00' : '#94a3b8' }}
            >
              25
            </button>
            <button
              className={`ma-btn ${showMA.ma99 ? 'active' : ''}`}
              onClick={() => setShowMA(prev => ({ ...prev, ma99: !prev.ma99 }))}
              style={{ color: showMA.ma99 ? '#9C27B0' : '#94a3b8' }}
            >
              99
            </button>
          </div>
        </div>

        {coinData && (
          <div className="chart-info">
            <div className="info-item">
              <span className="info-label">High:</span>
              <span className="info-value positive">${coinData.current_price ? (coinData.current_price * 1.02).toFixed(2) : '-'}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Low:</span>
              <span className="info-value negative">${coinData.current_price ? (coinData.current_price * 0.98).toFixed(2) : '-'}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Volume:</span>
              <span className="info-value">{coinData.volume ? coinData.volume.toLocaleString('en-US', { maximumFractionDigits: 0 }) : '-'}</span>
            </div>
          </div>
        )}

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
          <div ref={chartContainerRef} style={{ width: '100%', height: '500px' }} />
        </div>
      </div>
    </div>
  );
};

export default CoinChartModal;
