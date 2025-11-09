import React from 'react';

const Navbar = ({ overviewCoins }) => {
  const formatVolume = (num) => {
    if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
    if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
    if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
    return num.toFixed(2);
  };

  return (
    <nav className="navbar">
      <div className="navbar-content">
        <div className="logo"><i className="fas fa-chart-line"></i> Crypto Analytics</div>
        <div className="nav-stats">
          <div className="nav-stat">
            <div className="nav-stat-label">Total Coins</div>
            <div className="nav-stat-value">{overviewCoins.length}</div>
          </div>
          <div className="nav-stat">
            <div className="nav-stat-label">24h Volume</div>
            <div className="nav-stat-value">
              ${formatVolume(overviewCoins.reduce((sum, c) => sum + (c.volume * c.current_price), 0))}
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
