import React, { useState } from 'react';

const OverviewSection = ({ overviewCoins }) => {
  const [search, setSearch] = useState('');
  const [sortOrder, setSortOrder] = useState(null);

  const filtered = overviewCoins.filter(c => {
    const s = c.symbol.replace('USDT', '').toLowerCase();
    const n = c.symbol.toLowerCase();
    return s.includes(search.toLowerCase()) || n.includes(search.toLowerCase());
  });

  const sorted = [...filtered].sort((a, b) => {
    if (!sortOrder) return 0;
    return sortOrder === 'asc' ? a.current_price - b.current_price : b.current_price - a.current_price;
  });

  const formatNumber = (num) => num.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 6
  });

  return (
    <>
      <div className="overview-controls" style={{ display: 'flex', gap: '10px', marginTop: '20px', paddingBottom: '20px' }}>
        <input
          type="text"
          placeholder="코인 검색 (Overview)"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{
            padding: '8px 12px',
            borderRadius: '8px',
            border: '1px solid #444',
            background: '#1e1e2f',
            color: 'white',
            flex: 1
          }}
        />
        <button
          className="btn btn-info"
          onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
        >
          가격 {sortOrder === 'asc' ? '오름차순' : '내림차순'}
        </button>
      </div>

      <div className="market-overview">
        {sorted.map(coin => (
          <div key={coin.symbol} className="overview-card">
            <div className="overview-title">{coin.symbol.replace('USDT', '')}</div>
            <div className="overview-value">${formatNumber(coin.current_price)}</div>
            <div className={`overview-change ${coin.price_change_percent >= 0 ? 'positive' : 'negative'}`}>
              {coin.price_change_percent.toFixed(2)}%
            </div>
          </div>
        ))}
      </div>
    </>
  );
};

export default OverviewSection;
