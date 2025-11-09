import React, { useState } from 'react';
import ReactPaginate from 'react-paginate';

const LivePriceSection = ({ tableCoins, loadPrices, page, totalItems, limit, lastUpdate }) => {
  const [search, setSearch] = useState('');
  const [sortOrder, setSortOrder] = useState(null);

  const filtered = tableCoins.filter(c =>
    c.symbol.toLowerCase().includes(search.toLowerCase())
  );

  const sorted = [...filtered].sort((a, b) => {
    if (!sortOrder) return 0;
    return sortOrder === 'asc' ? a.current_price - b.current_price : b.current_price - a.current_price;
  });

  const formatNumber = (num) => num.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 6
  });

  const formatVolume = (num) => {
    if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
    if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
    if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
    return num.toFixed(2);
  };

  return (
    <div className="coin-table">
      <div className="table-header">
        <h2 className="table-title"><i className="fas fa-coins"></i> Live Prices</h2>
      </div>

      <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
        <input
          type="text"
          placeholder="코인 검색 (Live)"
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
        <button className="btn btn-info" onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}>
          가격 {sortOrder === 'asc' ? '오름차순' : '내림차순'}
        </button>
      </div>

      <div className="coin-list">
        {sorted.map(coin => {
          const symbol = coin.symbol.replace('USDT', '');
          return (
            <div key={coin.symbol} className="coin-item">
              <div className="coin-name">{symbol}</div>
              <div className="coin-price">${formatNumber(coin.current_price)}</div>
              <div className={`coin-change ${coin.price_change_percent >= 0 ? 'positive' : 'negative'}`}>
                {coin.price_change_percent.toFixed(2)}%
              </div>
              <div className="coin-volume">Vol: {formatVolume(coin.volume)}</div>
            </div>
          );
        })}
      </div>

      <div className="pagination-container">
        <ReactPaginate
          previousLabel={"<"}
          nextLabel={">"}
          breakLabel={"..."}
          pageCount={Math.ceil(totalItems / limit)}
          marginPagesDisplayed={2}
          pageRangeDisplayed={5}
          onPageChange={(e) => loadPrices(e.selected + 1)}
          containerClassName={"pagination"}
          activeClassName={"active"}
        />
      </div>

      <div className="last-update"><i className="fas fa-clock"></i> Last updated: {lastUpdate}</div>
    </div>
  );
};

export default LivePriceSection;
