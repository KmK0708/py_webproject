import React, { useState, useEffect } from 'react';
import '../styles/NewsSection.css';

const NewsSection = () => {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedSource, setSelectedSource] = useState('all');
  const [limit, setLimit] = useState(20);

  // 뉴스 로드
  const loadNews = async () => {
    setLoading(true);
    setError(null);

    try {
      const sourceParam = selectedSource !== 'all' ? `&source=${selectedSource}` : '';
      const response = await fetch(
        `http://localhost:5000/api/news?limit=${limit}${sourceParam}`
      );
      const data = await response.json();

      if (data.success) {
        setNews(data.data);
      } else {
        setError(data.error || '뉴스를 불러올 수 없습니다.');
      }
    } catch (err) {
      setError('뉴스를 불러오는 중 오류가 발생했습니다.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // 뉴스 크롤링 (수동)
  const scrapeNews = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/scrape-news?limit=10');
      const data = await response.json();

      if (data.success) {
        alert(`✅ ${data.saved_count}개의 새로운 뉴스를 수집했습니다!`);
        loadNews(); // 뉴스 목록 새로고침
      } else {
        alert('뉴스 수집 실패: ' + data.error);
      }
    } catch (err) {
      alert('뉴스 수집 중 오류가 발생했습니다.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // 컴포넌트 마운트 시 뉴스 로드
  useEffect(() => {
    loadNews();
  }, [selectedSource, limit]);

  // 시간 포맷팅
  const formatTime = (isoString) => {
    if (!isoString) return '';

    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 60) return `${diffMins}분 전`;
    if (diffHours < 24) return `${diffHours}시간 전`;
    if (diffDays < 7) return `${diffDays}일 전`;

    return date.toLocaleDateString('ko-KR');
  };

  // 소스별 색상
  const getSourceColor = (source) => {
    switch (source) {
      case 'CoinDesk': return '#f7931a';
      case 'CryptoNews': return '#26a69a';
      case 'CoinTelegraph': return '#3b82f6';
      default: return '#94a3b8';
    }
  };

  return (
    <div className="news-section">
      <div className="news-header">
        <div className="news-title-area">
          <h2>📰 Crypto News</h2>
          <span className="news-count">{news.length}개 뉴스</span>
        </div>

        <div className="news-controls">
          {/* 소스 필터 */}
          <select
            value={selectedSource}
            onChange={(e) => setSelectedSource(e.target.value)}
            className="news-filter"
          >
            <option value="all">모든 소스</option>
            <option value="CoinDesk">CoinDesk</option>
            <option value="CryptoNews">CryptoNews</option>
            <option value="CoinTelegraph">CoinTelegraph</option>
          </select>

          {/* 개수 선택 */}
          <select
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
            className="news-filter"
          >
            <option value={10}>10개</option>
            <option value={20}>20개</option>
            <option value={50}>50개</option>
          </select>

          {/* 새로고침 버튼 */}
          <button onClick={loadNews} className="news-btn" disabled={loading}>
            <i className="fas fa-sync-alt"></i> 새로고침
          </button>

          {/* 뉴스 수집 버튼 */}
          <button onClick={scrapeNews} className="news-btn scrape-btn" disabled={loading}>
            <i className="fas fa-download"></i> 뉴스 수집
          </button>
        </div>
      </div>

      {/* 로딩 */}
      {loading && (
        <div className="news-loading">
          <div className="spinner"></div>
          <p>뉴스를 불러오는 중...</p>
        </div>
      )}

      {/* 에러 */}
      {error && (
        <div className="news-error">
          <i className="fas fa-exclamation-triangle"></i>
          <p>{error}</p>
        </div>
      )}

      {/* 뉴스 리스트 */}
      {!loading && !error && news.length === 0 && (
        <div className="news-empty">
          <i className="fas fa-newspaper"></i>
          <p>아직 뉴스가 없습니다. "뉴스 수집" 버튼을 클릭하세요!</p>
        </div>
      )}

      {!loading && !error && news.length > 0 && (
        <div className="news-list">
          {news.map((item) => (
            <div key={item.id} className="news-card">
              <div className="news-card-header">
                <span
                  className="news-source"
                  style={{ color: getSourceColor(item.source) }}
                >
                  {item.source}
                </span>
                <span className="news-time">{formatTime(item.published_at)}</span>
              </div>

              <a
                href={item.url}
                target="_blank"
                rel="noopener noreferrer"
                className="news-title"
              >
                {item.title}
              </a>

              {item.related_coins && item.related_coins.length > 0 && (
                <div className="news-coins">
                  {item.related_coins.map((coin, idx) => (
                    <span key={idx} className="coin-badge">
                      {coin}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default NewsSection;
