// src/Components/Searchbar.jsx
import React from 'react';

const Searchbar = ({ value, onChange, onToggleSort, sortOrder, placeholder }) => {
  return (
    <div className="search-sort-container" style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
      <input
        type="text"
        placeholder={placeholder || "검색"}
        value={value}
        onChange={(e) => onChange(e.target.value)}
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
        onClick={onToggleSort}
      >
        <i className={`fas fa-sort-${sortOrder === 'asc' ? 'amount-up' : 'amount-down'}`}></i>
        &nbsp; 가격 {sortOrder === 'asc' ? '오름차순' : '내림차순'}
      </button>
    </div>
  );
};

export default Searchbar;
